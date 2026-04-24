"""
Black2 API Routes Module with X402 Integration

Provides all API endpoints for transaction management, wallet operations, and referrals.
Integrates with X402 protocol for escrow payments.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
import hashlib
import asyncio
import aiosqlite
import os
from datetime import datetime, timedelta

from src.db.transaction_db import (
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction_status,
    update_anchor_hash,
    get_or_create_wallet,
    add_referral_reward,
    settle_referral_rewards,
    cancel_referral_rewards,
    calculate_referral_chain,
    DB_PATH
)
from src.crypto.hash_service import sign_transaction, verify_transaction, sha256_hash, generate_keypair
from src.utils.rate_limiter import rate_limiter

router = APIRouter()


class TransactionCreate(BaseModel):
    from_address: str
    to_address: str
    amount: float
    currency: str = "USDT"
    contract_hash: str
    file_hash: Optional[str] = None
    referrer_address: Optional[str] = None
    use_x402_escrow: bool = False

class TransactionResponse(BaseModel):
    id: int
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    currency: str
    contract_hash: str
    file_hash: Optional[str] = None
    status: str
    timestamp: Optional[str] = None
    hash: str
    signature: str
    anchor_hash: Optional[str] = None
    anchored_at: Optional[str] = None
    referrer_address: Optional[str] = None
    referral_level: Optional[int] = 0
    x402_escrow_id: Optional[str] = None
    x402_escrow_address: Optional[str] = None
    x402_status: Optional[str] = None

class TransactionStatusUpdate(BaseModel):
    status: str
    file_hash: Optional[str] = None

class WalletWithdraw(BaseModel):
    withdraw_address: str
    amount: float

class WalletResponse(BaseModel):
    address: str
    balance: float
    total_earned: float
    referral_count: int


async def _initiate_x402_escrow(
    sender: str,
    receiver: str,
    amount: float,
    asset: str = "USDT"
) -> Dict[str, Any]:
    """
    Initiate X402 escrow for a transaction.
    HOOK: This integrates with X402 Bridge for escrow payment.
    """
    try:
        from src.x402.bridge import x402_bridge
        
        if not x402_bridge.is_available():
            return {
                "escrow_id": None,
                "escrow_address": None,
                "status": "mock"
            }
        
        result = await x402_bridge.initiate_escrow(
            sender=sender,
            receiver=receiver,
            amount=amount,
            asset=asset
        )
        
        return {
            "escrow_id": result.escrow_id,
            "escrow_address": result.escrow_address,
            "status": result.status
        }
        
    except ImportError:
        print("[X402] X402 Bridge not found, using mock escrow")
        return {
            "escrow_id": f"mock_escrow_{int(datetime.now().timestamp())}",
            "escrow_address": f"0x{''.join(random_hex(40))}",
            "status": "mock"
        }
    except Exception as e:
        print(f"[X402] Error initiating escrow: {e}")
        return {
            "escrow_id": None,
            "escrow_address": None,
            "status": "error"
        }


def random_hex(length: int) -> list:
    """Generate random hex characters"""
    import random
    return [random.choice('0123456789abcdef') for _ in range(length)]


@router.post("/api/v1/transactions", response_model=TransactionResponse)
async def create_new_transaction(transaction: TransactionCreate) -> TransactionResponse:
    """
    Create a new transaction and deduct payment from buyer's wallet.
    Optionally integrates with X402 for escrow payment.
    
    - **from_address**: Sender's address
    - **to_address**: Recipient's address
    - **amount**: Transaction amount
    - **currency**: Currency type (default: USDT)
    - **contract_hash**: Hash of the contract
    - **file_hash**: Optional hash of associated file
    - **referrer_address**: Optional referrer address
    - **use_x402_escrow**: Whether to use X402 escrow (default: False)
    """
    tx_id = str(uuid.uuid4())
    
    x402_escrow_id = None
    x402_escrow_address = None
    x402_status = None
    
    if transaction.use_x402_escrow:
        escrow_result = await _initiate_x402_escrow(
            sender=transaction.from_address,
            receiver=transaction.to_address,
            amount=transaction.amount,
            asset=transaction.currency
        )
        x402_escrow_id = escrow_result.get("escrow_id")
        x402_escrow_address = escrow_result.get("escrow_address")
        x402_status = escrow_result.get("status")
        print(f"[X402] Escrow initiated for {tx_id}: {x402_escrow_id}")
        
        if not x402_escrow_id:
            x402_status = "failed"
            print(f"[X402] WARNING: Escrow initiation failed for {tx_id}, marking transaction as pending")
    
    async with aiosqlite.connect(DB_PATH) as db:
        if not transaction.use_x402_escrow:
            result = await db.execute(
                'UPDATE ai_wallets SET balance = balance - ? WHERE address = ? AND balance >= ?',
                (transaction.amount, transaction.from_address, transaction.amount)
            )
            await db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=400, detail="Insufficient balance or wallet not found")
            print(f"[Payment] Deducted {transaction.amount} from AI wallet {transaction.from_address}")
    
    escrow_failed = transaction.use_x402_escrow and not x402_escrow_id
    tx_status = "pending" if escrow_failed else "paid"
    
    tx_data = {
        "tx_id": tx_id,
        "from_address": transaction.from_address,
        "to_address": transaction.to_address,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "contract_hash": transaction.contract_hash,
        "file_hash": transaction.file_hash,
        "status": tx_status,
        "referrer_address": transaction.referrer_address,
        "x402_escrow_id": x402_escrow_id,
        "x402_escrow_address": x402_escrow_address,
        "x402_status": x402_status
    }
    
    dummy_private_key = "0000000000000000000000000000000000000000000000000000000000000000"
    signed_tx = sign_transaction(tx_data, dummy_private_key)
    
    created_tx = await create_transaction(signed_tx)
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT tu1, tu2, tu3 FROM users WHERE address = ?',
            (transaction.to_address,)
        )
        seller = await cursor.fetchone()
        
        if seller:
            tu1_addr, tu2_addr, tu3_addr = seller[0], seller[1], seller[2]
            
            tu1_amount = round(transaction.amount * 0.05, 2) if tu1_addr else 0
            tu2_amount = round(transaction.amount * 0.03, 2) if tu2_addr else 0
            tu3_amount = round(transaction.amount * 0.02, 2) if tu3_addr else 0
            
            seller_amount = round(transaction.amount * 0.90, 2)
            
            total_commission = seller_amount + tu1_amount + tu2_amount + tu3_amount
            if total_commission > transaction.amount:
                ratio = transaction.amount / total_commission
                seller_amount = round(seller_amount * ratio, 2)
                tu1_amount = round(tu1_amount * ratio, 2)
                tu2_amount = round(tu2_amount * ratio, 2)
                tu3_amount = round(tu3_amount * ratio, 2)
            
            try:
                from src.utils.batch_writer import referral_writer
                
                await referral_writer.add(
                    '''INSERT INTO transaction_referrals
                       (tx_id, tu1_address, tu1_amount, tu2_address, tu2_amount,
                        tu3_address, tu3_amount, settlement_status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (tx_id, tu1_addr or '', tu1_amount or 0,
                     tu2_addr or '', tu2_amount or 0,
                     tu3_addr or '', tu3_amount or 0,
                     'pending')
                )
            except Exception as e:
                print(f"[Order] Failed to queue referral pre-write: {e}")
    
    try:
        from src.anchor.auto_confirm import auto_confirm_service
        
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                'SELECT reputation_score FROM users WHERE address = ?',
                (transaction.from_address,)
            )
            user = await cursor.fetchone()
            reputation = user[0] if user else 100
        
        if reputation >= 95:
            auto_confirm_hours = 24
        elif reputation >= 85:
            auto_confirm_hours = 48
        else:
            auto_confirm_hours = 72
        
        await auto_confirm_service.start_countdown(
            tx_id=tx_id,
            auto_confirm_hours=auto_confirm_hours
        )
    except Exception as e:
        print(f"[AutoConfirm] Failed to start countdown: {e}")
    
    return TransactionResponse(**created_tx)


@router.get("/api/v1/transactions/{tx_id}", response_model=TransactionResponse)
async def get_transaction_by_id(tx_id: str) -> TransactionResponse:
    """Get a transaction by its ID."""
    transaction = await get_transaction(tx_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse(**transaction)


@router.get("/api/v1/transactions", response_model=List[TransactionResponse])
async def list_all_transactions(
    status: Optional[str] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[TransactionResponse]:
    """List transactions with optional filters."""
    transactions = await list_transactions(
        status=status,
        from_address=from_address,
        to_address=to_address,
        limit=limit,
        offset=offset
    )
    return [TransactionResponse(**tx) for tx in transactions]


@router.post("/api/v1/transactions/{tx_id}/verify")
async def verify_transaction_endpoint(tx_id: str, verification: Dict[str, str]) -> Dict[str, Any]:
    """Verify a transaction's signature."""
    transaction = await get_transaction(tx_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    public_key = verification.get("public_key", "")
    result = verify_transaction(transaction, public_key)
    return result


@router.put("/api/v1/transactions/{tx_id}/status")
async def update_transaction_status_endpoint(tx_id: str, update: TransactionStatusUpdate) -> Dict[str, bool]:
    """Update transaction status."""
    success = await update_transaction_status(
        tx_id=tx_id,
        status=update.status,
        file_hash=update.file_hash
    )
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"updated": success}


@router.get("/api/v1/wallet/{address}", response_model=WalletResponse)
async def get_wallet(address: str) -> WalletResponse:
    """Get AI wallet balance and details."""
    wallet = await get_or_create_wallet(address)
    return WalletResponse(**wallet)


@router.post("/api/v1/wallet/{address}/withdraw")
async def withdraw_from_wallet(address: str, withdraw: WalletWithdraw) -> Dict[str, Any]:
    """
    Request a withdrawal from AI wallet.
    Minimum withdrawal: 50 USDT
    """
    if withdraw.amount < 50:
        raise HTTPException(status_code=400, detail="Minimum withdrawal amount is 50 USDT")
    
    wallet = await get_or_create_wallet(address)
    
    if wallet["balance"] < withdraw.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    return {
        "message": "Withdrawal request submitted",
        "address": address,
        "withdraw_address": withdraw.withdraw_address,
        "amount": withdraw.amount
    }


@router.get("/api/v1/x402/balance/{agent_id}")
async def get_x402_balance(agent_id: str) -> Dict[str, Any]:
    """Get X402 balance for an agent."""
    try:
        from src.x402.bridge import x402_bridge
        
        if not x402_bridge.is_available():
            return {
                "agent_id": agent_id,
                "available": 0,
                "locked": 0,
                "total": 0,
                "status": "unavailable"
            }
        
        balance = await x402_bridge.check_balance(agent_id)
        return balance
        
    except ImportError:
        return {
            "agent_id": agent_id,
            "error": "X402 Bridge not found"
        }
    except Exception as e:
        return {
            "agent_id": agent_id,
            "error": str(e)
        }


@router.post("/api/v1/x402/escrow/{tx_id}/release")
async def release_x402_escrow(tx_id: str, release_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Manually release X402 escrow for a transaction.
    Usually called by arbitration timer, but can be called manually for manual releases.
    """
    verdict = release_data.get("verdict", "seller_wins")
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT x402_escrow_id, from_address, to_address FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        tx = await cursor.fetchone()
        
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        escrow_id, buyer_addr, seller_addr = tx
        
        if not escrow_id:
            raise HTTPException(status_code=400, detail="No X402 escrow for this transaction")
    
    recipient = buyer_addr if verdict == "buyer_wins" else seller_addr
    
    try:
        from src.x402.bridge import x402_bridge
        
        if not x402_bridge.is_available():
            return {
                "success": False,
                "message": "X402 Bridge not available"
            }
        
        result = await x402_bridge.release_funds(
            escrow_id=escrow_id,
            recipient=recipient,
            verdict=verdict
        )
        
        return {
            "success": result.success,
            "tx_hash": result.tx_hash,
            "recipient": result.recipient,
            "verdict": result.verdict,
            "message": result.message
        }
        
    except ImportError:
        return {
            "success": False,
            "message": "X402 Bridge not found"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/api/v1/transactions/{tx_id}/escrow_status")
async def get_transaction_escrow_status(tx_id: str) -> Dict[str, Any]:
    """
    Get X402 escrow status for a transaction.
    Queries the X402 chain for real-time fund lock status.
    
    - **tx_id**: Transaction ID to query
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT x402_escrow_id, x402_escrow_address, x402_status, amount, currency FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        tx = await cursor.fetchone()
        
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
    
    escrow_id, escrow_address, local_status, amount, currency = tx
    
    if not escrow_id:
        raise HTTPException(status_code=400, detail="No X402 escrow for this transaction")
    
    try:
        from src.x402.bridge import x402_bridge
        
        if not x402_bridge.is_available():
            return {
                "tx_id": tx_id,
                "escrow_id": escrow_id,
                "escrow_address": escrow_address,
                "status": local_status or "unknown",
                "locked_amount": amount,
                "asset": currency,
                "on_chain": False,
                "message": "X402 Bridge not available, returning local status"
            }
        
        chain_status = await x402_bridge.get_escrow_status(escrow_id)
        
        return {
            "tx_id": tx_id,
            "escrow_id": escrow_id,
            "escrow_address": escrow_address,
            "status": chain_status.get("status", local_status),
            "locked_amount": chain_status.get("locked_amount", amount),
            "asset": chain_status.get("asset", currency),
            "on_chain": chain_status.get("on_chain", True),
            "last_updated": chain_status.get("last_updated")
        }
        
    except ImportError:
        return {
            "tx_id": tx_id,
            "escrow_id": escrow_id,
            "escrow_address": escrow_address,
            "status": local_status,
            "locked_amount": amount,
            "asset": currency,
            "on_chain": False,
            "message": "X402 Bridge not found"
        }
    except Exception as e:
        return {
            "tx_id": tx_id,
            "escrow_id": escrow_id,
            "escrow_address": escrow_address,
            "status": local_status,
            "locked_amount": amount,
            "asset": currency,
            "on_chain": False,
            "error": str(e)
        }
