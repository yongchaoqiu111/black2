"""
Black2 API Routes Module

Provides all API endpoints for transaction management, wallet operations, and referrals.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
import hashlib
import random
import string
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
    get_or_create_human_wallet,
    add_referral_reward,
    settle_referral_rewards,
    cancel_referral_rewards,
    calculate_referral_chain,
    add_referral_relationship,
    record_deposit,
    confirm_deposit,
    record_withdrawal,
    complete_withdrawal,
    create_product,
    get_product,
    list_products,
    update_product_status,
    create_contract,
    update_contract_anchor,
    update_contract_status,
    get_contract,
    apply_transaction_reputation_update,
    get_user_reputation,
    get_user_reputation_snapshot,
    update_reputation_cache_batch
)
from src.db.transaction_db import DB_PATH
from src.crypto.hash_service import sign_transaction, verify_transaction, sha256_hash, generate_keypair, sign_message, verify_signature
from src.crypto.hd_wallet import hd_wallet_service
from src.agents.arbitration_engine import arbitration_engine
from src.contract.templates import (
    get_template,
    list_templates,
    generate_contract_hash,
    validate_contract_against_template,
    detect_effect_promise
)
from src.anchor.github_anchor import GitHubAnchorService
from src.utils.websocket_manager import websocket_manager
from src.utils.rate_limiter import rate_limiter
from fastapi import WebSocket, WebSocketDisconnect

# Initialize GitHub Anchor Service
try:
    github_anchor = GitHubAnchorService()
except ValueError:
    # If no GitHub token, create a dummy instance for API docs
    github_anchor = None

router = APIRouter()


# Pydantic models for request/response bodies
class TransactionCreate(BaseModel):
    from_address: str
    to_address: str
    amount: float
    currency: str = "USDT"
    contract_hash: str
    file_hash: Optional[str] = None
    referrer_address: Optional[str] = None

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
    # Referral commission fields (from transaction_referrals table)
    tu1_address: Optional[str] = None
    tu1_amount: Optional[float] = 0
    tu2_address: Optional[str] = None
    tu2_amount: Optional[float] = 0
    tu3_address: Optional[str] = None
    tu3_amount: Optional[float] = 0
    settlement_status: Optional[str] = None
    # X402 Integration fields
    x402_escrow_id: Optional[str] = None
    x402_escrow_address: Optional[str] = None
    x402_status: Optional[str] = None

class TransactionVerify(BaseModel):
    public_key: str

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

class ReferralResponse(BaseModel):
    address: str
    referrals: List[str]


@router.post("/api/v1/transactions", response_model=TransactionResponse)
async def create_new_transaction(transaction: TransactionCreate) -> TransactionResponse:
    """
    Create a new transaction and deduct payment from buyer's wallet.
    
    - **from_address**: Sender's address
    - **to_address**: Recipient's address
    - **amount**: Transaction amount
    - **currency**: Currency type (default: USDT)
    - **contract_hash**: Hash of the contract
    - **file_hash**: Optional hash of associated file
    - **referrer_address**: Optional referrer address
    """
    # Generate a unique transaction ID
    tx_id = str(uuid.uuid4())
    
    # [X402 Integration] Initiate Escrow Payment (No Registration Mode)
    # Instead of deducting from local balance, we lock funds via X402 Relay Network.
    try:
        from src.x402.bridge import x402_bridge
        escrow_result = await x402_bridge.initiate_escrow(
            sender=transaction.from_address,
            receiver=transaction.to_address,
            amount=transaction.amount,
            asset=transaction.currency
        )
        print(f"[X402] Escrow initiated: {escrow_result.escrow_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"X402 Escrow failed: {str(e)}")
    
    # Create transaction data with status 'paid' and X402 details
    tx_data = {
        "tx_id": tx_id,
        "from_address": transaction.from_address,
        "to_address": transaction.to_address,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "contract_hash": transaction.contract_hash,
        "file_hash": transaction.file_hash,
        "status": "paid",  # Changed from 'pending' to 'paid'
        "referrer_address": transaction.referrer_address,
        "x402_escrow_id": escrow_result.escrow_id,
        "x402_escrow_address": escrow_result.escrow_address,
        "x402_status": escrow_result.status
    }
    
    # For demo purposes, use a dummy private key
    dummy_private_key = "0000000000000000000000000000000000000000000000000000000000000000"
    signed_tx = sign_transaction(tx_data, dummy_private_key)
    
    # Save to database
    created_tx = await create_transaction(signed_tx)
    
    # Query SELLER's referral chain and push to async queue
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT tu1, tu2, tu3 FROM users WHERE address = ?',
            (transaction.to_address,)  # to_address is seller
        )
        seller = await cursor.fetchone()
        
        if seller:
            tu1_addr = seller[0]
            tu2_addr = seller[1]
            tu3_addr = seller[2]
            
            # Calculate reward amounts (round to 2 decimal places, ensure total doesn't exceed order amount)
            tu1_amount = round(transaction.amount * 0.05, 2) if tu1_addr else 0
            tu2_amount = round(transaction.amount * 0.03, 2) if tu2_addr else 0
            tu3_amount = round(transaction.amount * 0.02, 2) if tu3_addr else 0
            
            # Seller gets 90%
            seller_amount = round(transaction.amount * 0.90, 2)
            
            # Ensure total commission doesn't exceed order amount
            total_commission = seller_amount + tu1_amount + tu2_amount + tu3_amount
            if total_commission > transaction.amount:
                # Adjust proportionally if rounding causes overflow
                ratio = transaction.amount / total_commission
                seller_amount = round(seller_amount * ratio, 2)
                tu1_amount = round(tu1_amount * ratio, 2)
                tu2_amount = round(tu2_amount * ratio, 2)
                tu3_amount = round(tu3_amount * ratio, 2)
            
            # Async Pre-write: Use BatchWriter to reduce DB pressure
            # This only records WHO gets HOW MUCH, does NOT credit wallets yet
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
                print(f"[Order] {tx_id} - Referral pre-write queued (seller: {seller_amount}, tu1: {tu1_amount}, tu2: {tu2_amount}, tu3: {tu3_amount})")
            except Exception as e:
                print(f"[Order] Failed to queue referral pre-write: {e}")
        else:
            print(f"[Order] Warning: Seller {transaction.to_address} not found in users table")
    
    # Start auto-confirm countdown (default 72 hours)
    try:
        from src.anchor.auto_confirm import auto_confirm_service
        
        # Get buyer's reputation to determine auto-confirm time
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                'SELECT reputation_score FROM users WHERE address = ?',
                (transaction.from_address,)
            )
            user = await cursor.fetchone()
            reputation = user[0] if user else 100
        
        # Calculate auto-confirm hours based on reputation
        if reputation >= 95:
            auto_confirm_hours = 24  # High trust: 24 hours
        elif reputation >= 85:
            auto_confirm_hours = 48  # Medium trust: 48 hours
        else:
            auto_confirm_hours = 72  # Low trust: 72 hours
        
        # Start countdown
        await auto_confirm_service.start_countdown(
            tx_id=tx_id,
            auto_confirm_hours=auto_confirm_hours
        )
        
        print(f"[AutoConfirm] Started {auto_confirm_hours}h countdown for order {tx_id} (reputation: {reputation})")
    except Exception as e:
        print(f"[AutoConfirm] Failed to start countdown: {e}")
    
    return TransactionResponse(**created_tx)


@router.post("/api/v1/transactions/{tx_id}/complete")
async def complete_transaction(tx_id: str) -> Dict[str, Any]:
    """
    Complete a transaction and trigger async settlement.
    Call this when buyer confirms receipt or auto-confirm timeout.
    
    Rate limit: 1 request per 60 seconds
    
    Only allowed for 'paid' and 'shipped' status orders.
    """
    # Rate limiting
    allowed, remaining = rate_limiter.is_allowed(f"complete_{tx_id}", interval=1)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Wait {remaining}s"
        )
    
    # Check transaction status
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT status FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        current_status = row[0]
        
        # Only allow complete for 'paid' or 'shipped' status
        if current_status not in ['paid', 'shipped']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot complete transaction with status '{current_status}'. Only 'paid' or 'shipped' orders can be completed."
            )
    
    # Update transaction status
    await update_transaction_status(tx_id, 'completed')
    
    # Log this status change asynchronously
    try:
        from src.utils.batch_writer import log_writer
        await log_writer.add(
            'INSERT INTO reputation_history (user_address, score_change, new_score, reason) VALUES (?, ?, ?, ?)',
            ('SYSTEM', 0, 0, f'Transaction {tx_id} completed at {datetime.now().isoformat()}')
        )
    except Exception as e:
        print(f"[Log] Failed to queue status log: {e}")
    
    # Get referral info and execute settlement
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT tu1_address, tu1_amount, tu2_address, tu2_amount, tu3_address, tu3_amount FROM transaction_referrals WHERE tx_id = ?',
            (tx_id,)
        )
        order = await cursor.fetchone()
        
        if order:
            # Call the settlement function from transaction_db
            from src.db.transaction_db import settle_referral_rewards
            await settle_referral_rewards(tx_id)
            print(f"[Complete] Settlement completed for order {tx_id}")
        else:
            print(f"[Complete] Warning: No referral record found in transaction_referrals for {tx_id}")
    
    # Cancel auto-confirm countdown if exists
    try:
        from src.anchor.auto_confirm import auto_confirm_service
        await auto_confirm_service.cancel_countdown(tx_id)
    except:
        pass
    
    return {
        "message": "Transaction completed, settlement queued",
        "tx_id": tx_id
    }


@router.post("/api/v1/transactions/{tx_id}/dispute")
async def dispute_transaction(tx_id: str, dispute_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Initiate a dispute for a transaction.
    
    This freezes the transaction and starts a 48-hour evidence collection period.
    After 48 hours, the system will automatically arbitrate based on hash comparison.
    
    Rate limit: 1 request per 60 seconds
    
    Only allowed for 'paid' and 'shipped' status orders.
    """
    # Rate limiting
    allowed, remaining = rate_limiter.is_allowed(f"dispute_{tx_id}", interval=5)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Wait {remaining}s"
        )
    
    if dispute_data is None:
        dispute_data = {}
    
    reason = dispute_data.get('reason', '')
    
    if not reason:
        raise HTTPException(status_code=400, detail="Dispute reason is required")
    
    # Check transaction status and get details
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT status, from_address, to_address, amount, contract_hash, file_hash FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        current_status, buyer_addr, seller_addr, amount, contract_hash, file_hash = row
        
        # Only allow dispute for 'paid' or 'shipped' status
        if current_status not in ['paid', 'shipped', 'delivered', 'pending']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot dispute transaction with status '{current_status}'."
            )
        
        # Micro-transaction Instant Arbitration Logic
        is_micro = amount < 1.0  # Define micro-transaction threshold
        auto_refund_triggered = False
        
        if is_micro and contract_hash and file_hash:
            if contract_hash != file_hash:
                # Hash mismatch: Seller breached contract, instant refund
                print(f"[Micro-Arbitration] Hash mismatch detected for {tx_id}. Auto-refunding...")
                await db.execute('UPDATE transactions SET status = ? WHERE tx_id = ?', ('refunded', tx_id))
                await db.execute('UPDATE ai_wallets SET balance = balance + ? WHERE address = ?', (amount, buyer_addr))
                await db.execute('UPDATE users SET reputation_score = MAX(0, reputation_score - 5), dispute_count = dispute_count + 1 WHERE address = ?', (seller_addr,))
                auto_refund_triggered = True
            else:
                # Hash match: Buyer is likely malicious, reject dispute
                print(f"[Micro-Arbitration] Hashes match for {tx_id}. Dispute rejected.")
                return {
                    "message": "Dispute rejected. Delivery hash matches the contract hash.",
                    "tx_id": tx_id,
                    "status": current_status,
                    "verdict": "seller_wins"
                }

        if not auto_refund_triggered:
            # Standard dispute flow for high-value or missing hash cases
            await db.execute(
                'UPDATE transactions SET status = ? WHERE tx_id = ?',
                ('disputed', tx_id)
            )
            
            from datetime import datetime, timedelta
            deadline = datetime.now() + timedelta(hours=48)
            
            await db.execute('''
                INSERT INTO arbitration_records 
                (tx_id, buyer_address, seller_address, buyer_reason, status, deadline)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tx_id, buyer_addr, seller_addr, reason, 'evidence_collection', deadline.isoformat()))
        
        await db.commit()
    
    # Log dispute event asynchronously
    if not auto_refund_triggered:
        try:
            from src.utils.batch_writer import log_writer
            await log_writer.add(
                'INSERT INTO reputation_history (user_address, score_change, new_score, reason) VALUES (?, ?, ?, ?)',
                ('SYSTEM', 0, 0, f'Transaction {tx_id} disputed at {datetime.now().isoformat()}')
            )
        except Exception as e:
            print(f"[Log] Failed to queue dispute log: {e}")
        
        # Cancel auto-confirm countdown if exists
        try:
            from src.anchor.auto_confirm import auto_confirm_service
            await auto_confirm_service.cancel_countdown(tx_id)
            print(f"[Dispute] Cancelled auto-confirm countdown for order {tx_id}")
        except Exception as e:
            print(f"[Dispute] Failed to cancel countdown: {e}")
        
        # Start arbitration countdown
        try:
            from src.anchor.arbitration_timer import arbitration_timer_service
            await arbitration_timer_service.start_arbitration_countdown(tx_id, hours=48)
            print(f"[Arbitration] Started 48h countdown for order {tx_id}")
        except Exception as e:
            print(f"[Arbitration] Failed to start countdown: {e}")
    
    return {
        "message": "Dispute initiated. Transaction frozen. Seller has 48 hours to submit evidence." if not auto_refund_triggered else "Micro-transaction auto-refunded due to hash mismatch.",
        "tx_id": tx_id,
        "status": "refunded" if auto_refund_triggered else "disputed",
        "verdict": "buyer_wins" if auto_refund_triggered else None,
        "deadline": deadline.isoformat() if not auto_refund_triggered else None,
        "buyer_reason": reason
    }


@router.post("/api/v1/arbitration/{tx_id}/seller-evidence")
async def submit_seller_evidence(tx_id: str, evidence_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Seller submits evidence for arbitration.
    
    Args:
        tx_id: Transaction ID being disputed
        evidence_data: Evidence information (description, proof files, etc.)
    """
    if evidence_data is None:
        evidence_data = {}
    
    evidence = evidence_data.get('evidence', '')
    
    if not evidence:
        raise HTTPException(status_code=400, detail="Evidence is required")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if arbitration record exists
        cursor = await db.execute(
            'SELECT status, seller_address FROM arbitration_records WHERE tx_id = ?',
            (tx_id,)
        )
        record = await cursor.fetchone()
        
        if not record:
            raise HTTPException(status_code=404, detail="Arbitration record not found")
        
        status, seller_addr = record
        
        if status != 'evidence_collection':
            raise HTTPException(status_code=400, detail=f"Cannot submit evidence in status '{status}'")
        
        # Update seller evidence
        await db.execute(
            'UPDATE arbitration_records SET seller_evidence = ?, status = ? WHERE tx_id = ?',
            (evidence, 'arbitrating', tx_id)
        )
        await db.commit()
    
    print(f"[Arbitration] Seller submitted evidence for order {tx_id}")
    
    return {
        "message": "Evidence submitted successfully",
        "tx_id": tx_id,
        "status": "arbitrating"
    }


@router.get("/api/v1/arbitration/{tx_id}/status")
async def get_arbitration_status(tx_id: str) -> Dict[str, Any]:
    """
    Get arbitration status for a transaction.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM arbitration_records WHERE tx_id = ?',
            (tx_id,)
        )
        record = await cursor.fetchone()
        
        if not record:
            raise HTTPException(status_code=404, detail="Arbitration record not found")
        
        columns = [desc[0] for desc in cursor.description]
        arbitration = dict(zip(columns, record))
        
        return arbitration


@router.post("/api/v1/transactions/{tx_id}/refund")
async def request_refund(tx_id: str, refund_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Buyer requests a refund. Seller has 48 hours to approve or reject.
    If seller rejects or doesn't respond, arbitration is triggered.
    
    Rate limit: 1 request per 60 seconds
    
    Only allowed for 'paid', 'shipped', or 'delivered' status orders.
    """
    # Rate limiting
    allowed, remaining = rate_limiter.is_allowed(f"refund_{tx_id}", interval=5)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Wait {remaining}s"
        )
    
    if refund_data is None:
        refund_data = {}
    
    reason = refund_data.get('reason', '无理由')
    
    # Check transaction status and get details
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT status, from_address, to_address, amount FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        current_status, buyer_addr, seller_addr, amount = row
        
        # Only allow refund request for these statuses
        if current_status not in ['paid', 'shipped', 'delivered']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot request refund for status '{current_status}'."
            )
        
        # Update transaction status to 'refund_requested'
        await db.execute(
            'UPDATE transactions SET status = ? WHERE tx_id = ?',
            ('refund_requested', tx_id)
        )
        
        # Create refund request record
        from datetime import datetime, timedelta
        deadline = datetime.now() + timedelta(hours=48)
        
        await db.execute('''
            INSERT INTO arbitration_records 
            (tx_id, buyer_address, seller_address, buyer_reason, status, deadline)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tx_id, buyer_addr, seller_addr, reason, 'refund_pending', deadline.isoformat()))
        
        await db.commit()
    
    print(f"[Refund] Buyer requested refund for order {tx_id}, waiting for seller approval")
    
    return {
        "message": "Refund requested. Seller has 48 hours to approve or reject.",
        "tx_id": tx_id,
        "status": "refund_requested",
        "deadline": deadline.isoformat()
    }


@router.post("/api/v1/refunds/{tx_id}/approve")
async def approve_refund(tx_id: str) -> Dict[str, Any]:
    """
    Seller approves refund request. Money is returned to buyer immediately.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Check refund request status
        cursor = await db.execute(
            'SELECT status, from_address, to_address, amount FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        current_status, buyer_addr, seller_addr, amount = row
        
        if current_status != 'refund_requested':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve refund for status '{current_status}'."
            )
        
        # Refund to buyer's AI wallet (Atomic Operation)
        await db.execute(
            'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
            (amount, buyer_addr)
        )
        
        # Update transaction status to 'refunded'
        await db.execute(
            'UPDATE transactions SET status = ? WHERE tx_id = ?',
            ('refunded', tx_id)
        )
        
        # Cancel all pending referral rewards
        await db.execute('''
            UPDATE transaction_referrals 
            SET settlement_status = 'cancelled'
            WHERE tx_id = ?
        ''', (tx_id,))
        
        # Update arbitration record
        await db.execute('''
            UPDATE arbitration_records 
            SET status = 'completed', verdict = 'buyer_wins', 
                verdict_reason = 'Seller approved refund', resolved_at = ?
            WHERE tx_id = ?
        ''', (datetime.now().isoformat(), tx_id))
        
        # Increment dispute count for both parties (they had a dispute)
        await db.execute('''
            UPDATE users SET dispute_count = dispute_count + 1
            WHERE address IN (?, ?)
        ''', (buyer_addr, seller_addr))
        
        await db.commit()
    
    print(f"[Refund] Seller approved refund for order {tx_id}")
    
    return {
        "message": f"Refund approved. {amount} USDT returned to buyer.",
        "tx_id": tx_id,
        "status": "refunded"
    }


@router.post("/api/v1/refunds/{tx_id}/reject")
async def reject_refund(tx_id: str, reject_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Seller rejects refund request. Arbitration is triggered automatically.
    """
    if reject_data is None:
        reject_data = {}
    
    reason = reject_data.get('reason', '无理由拒绝')
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check refund request status
        cursor = await db.execute(
            'SELECT status, from_address, to_address, amount, contract_hash, file_hash FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        current_status, buyer_addr, seller_addr, amount, contract_hash, file_hash = row
        
        if current_status != 'refund_requested':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject refund for status '{current_status}'."
            )
        
        # Update transaction status to 'disputed'
        await db.execute(
            'UPDATE transactions SET status = ? WHERE tx_id = ?',
            ('disputed', tx_id)
        )
        
        # Update arbitration record to start arbitration
        await db.execute('''
            UPDATE arbitration_records 
            SET status = 'evidence_collection', seller_evidence = ?
            WHERE tx_id = ?
        ''', (reason, tx_id))
        
        await db.commit()
    
    # Start arbitration countdown (48 hours)
    try:
        from src.anchor.arbitration_timer import arbitration_timer_service
        await arbitration_timer_service.start_arbitration_countdown(tx_id, hours=48)
        print(f"[Arbitration] Started 48h countdown for order {tx_id} after seller rejection")
    except Exception as e:
        print(f"[Arbitration] Failed to start countdown: {e}")
    
    print(f"[Refund] Seller rejected refund for order {tx_id}, arbitration started")
    
    return {
        "message": "Refund rejected. Arbitration started.",
        "tx_id": tx_id,
        "status": "disputed"
    }


@router.post("/api/v1/transactions/{tx_id}/cancel")
async def cancel_transaction(tx_id: str) -> Dict[str, Any]:
    """
    Cancel a transaction and void referral rewards.
    
    Rate limit: 1 request per 60 seconds
    """
    # Rate limiting
    allowed, remaining = rate_limiter.is_allowed(f"cancel_{tx_id}", interval=5)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Wait {remaining}s"
        )
    
    # Update transaction status
    await update_transaction_status(tx_id, 'cancelled')
    
    # Cancel all pending referral rewards
    await cancel_referral_rewards(tx_id)
    
    return {
        "message": "Transaction cancelled",
        "tx_id": tx_id
    }


@router.get("/api/v1/transactions/{tx_id}", response_model=TransactionResponse)
async def get_transaction_by_id(tx_id: str) -> TransactionResponse:
    """
    Get a transaction by its ID.
    
    Rate limit: 1 request per 60 seconds
    """
    # Rate limiting
    allowed, remaining = rate_limiter.is_allowed(f"get_tx_{tx_id}", interval=5)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Wait {remaining}s"
        )
    
    transaction = await get_transaction(tx_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse(**transaction)


@router.get("/api/v1/transactions", response_model=List[TransactionResponse])
async def list_all_transactions(
    status: Optional[str] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[TransactionResponse]:
    """
    List transactions with optional filters.
    
    - **status**: Filter by transaction status
    - **from_address**: Filter by sender address
    - **to_address**: Filter by recipient address
    - **limit**: Maximum number of transactions to return (default: 50, max: 100)
    - **offset**: Offset for pagination (default: 0)
    
    Rate limit: 1 request per 60 seconds per IP
    """
    # Apply rate limiting (60 seconds per request)
    client_ip = "unknown"  # In production, get from request headers
    allowed, remaining = rate_limiter.is_allowed(f"list_tx_{client_ip}", interval=5)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Please wait {remaining} seconds before next query."
        )
    
    transactions = await list_transactions(
        status=status,
        from_address=from_address,
        to_address=to_address,
        limit=limit,
        offset=offset
    )
    return [TransactionResponse(**tx) for tx in transactions]


@router.post("/api/v1/transactions/{tx_id}/verify")
async def verify_transaction_endpoint(tx_id: str, verification: TransactionVerify) -> Dict[str, Any]:
    """
    Verify a transaction's signature.
    
    - **public_key**: Public key to verify the signature
    """
    transaction = await get_transaction(tx_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    result = verify_transaction(transaction, verification.public_key)
    return result


@router.put("/api/v1/transactions/{tx_id}/status")
async def update_transaction_status_endpoint(tx_id: str, update: TransactionStatusUpdate) -> Dict[str, Any]:
    """
    Update transaction status with automatic reputation and referral settlement.
    
    When status changes to 'completed':
    - Settles pending referral rewards
    - Updates seller reputation (+1 point)
    
    When status changes to 'refunded':
    - Cancels pending referral rewards
    - Updates seller reputation (-5 to -20 points based on reason)
    
    - **status**: New status for the transaction
    - **file_hash**: Optional file hash to update
    """
    # Get current transaction
    tx = await get_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    old_status = tx.get('status')
    new_status = update.status
    
    # Update status
    success = await update_transaction_status(
        tx_id=tx_id,
        status=new_status,
        file_hash=update.file_hash
    )
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    result = {"updated": True, "old_status": old_status, "new_status": new_status}
    
    # Handle automatic actions based on status change
    if new_status == 'completed' and old_status != 'completed':
        # 1. Settle referral rewards
        try:
            await settle_referral_rewards(tx_id)
            result["referral_settled"] = True
        except Exception as e:
            result["referral_settled"] = False
            result["referral_error"] = str(e)
        
        # 2. Update seller reputation
        try:
            await apply_transaction_reputation_update(tx_id, 'completed')
            seller_address = tx.get('to_address', '')
            if seller_address:
                seller_rep = await get_user_reputation(seller_address)
                result["seller_reputation"] = seller_rep
        except Exception as e:
            result["reputation_error"] = str(e)
    
    elif new_status in ['refunded', 'cancelled'] and old_status not in ['refunded', 'cancelled']:
        # 1. Cancel referral rewards
        try:
            await cancel_referral_rewards(tx_id)
            result["referral_cancelled"] = True
        except Exception as e:
            result["referral_cancelled"] = False
            result["referral_error"] = str(e)
        
        # 2. Update seller reputation (negative)
        try:
            await apply_transaction_reputation_update(tx_id, 'refunded')
            seller_address = tx.get('to_address', '')
            if seller_address:
                seller_rep = await get_user_reputation(seller_address)
                result["seller_reputation"] = seller_rep
        except Exception as e:
            result["reputation_error"] = str(e)
    
    return result


@router.get("/api/v1/reputation/{address}")
async def get_reputation(address: str) -> Dict[str, Any]:
    """
    Get user's reputation snapshot (O(1) Cache Read).
    Optimized for high-frequency micro-transactions.
    """
    rep = await get_user_reputation_snapshot(address)
    return rep


@router.get("/api/v1/wallet/{address}", response_model=WalletResponse)
async def get_wallet(address: str) -> WalletResponse:
    """
    Get AI wallet balance and details.
    """
    wallet = await get_or_create_wallet(address)
    return WalletResponse(**wallet)


@router.get("/api/v1/wallets/human/{address}")
async def get_human_wallet(address: str) -> Dict[str, Any]:
    """
    Get human wallet with points balance.
    
    Returns human-readable wallet information including:
    - Points balance
    - Locked points
    - Total deposited/withdrawn
    """
    wallet = await get_or_create_human_wallet(address)
    return {
        "address": wallet['address'],
        "points_balance": wallet['points_balance'],
        "locked_points": wallet['locked_points'],
        "total_deposited": wallet['total_deposited'],
        "total_withdrawn": wallet['total_withdrawn'],
        "created_at": wallet['created_at']
    }


@router.get("/api/v1/wallets/ai/{address}")
async def get_ai_wallet(address: str) -> Dict[str, Any]:
    """
    Get AI wallet with balance.
    
    AI wallets receive referral commissions automatically.
    
    Rate limit: 1 request per 5 seconds (development), 60 seconds (production)
    """
    # Rate limiting - use 5s for development, 60s for production
    import os
    interval = int(os.getenv('RATE_LIMIT_INTERVAL', '5'))  # Default 5s for dev
    allowed, remaining = rate_limiter.is_allowed(f"ai_wallet_{address}", interval=interval)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Wait {remaining}s"
        )
    
    wallet = await get_or_create_wallet(address)
    return {
        "address": wallet['address'],
        "balance": wallet['balance'],
        "total_earned": wallet['total_earned'],
        "referral_count": wallet['referral_count'],
        "created_at": wallet['created_at']
    }


@router.get("/api/v1/wallets/ai/generate")
async def generate_ai_wallet(ai_index: int = Query(0, ge=0)) -> Dict[str, Any]:
    """
    Generate AI sub-wallet from master wallet.
    
    Args:
        ai_index: Unique index for this AI (starts from 0)
        
    Returns:
        dict: AI wallet information (address only, no private key)
    """
    try:
        wallet_info = hd_wallet_service.generate_ai_wallet(ai_index)
        
        # Create or get wallet in database
        wallet = await get_or_create_wallet(wallet_info['address'])
        
        return {
            "success": True,
            "wallet": {
                "address": wallet_info['address'],
                "path": wallet_info['path'],
                "index": wallet_info['index'],
                "master_address": wallet_info['master_address']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate wallet: {str(e)}")


@router.post("/api/v1/wallet/{address}/withdraw")
async def withdraw_from_wallet(address: str, withdraw: WalletWithdraw) -> Dict[str, Any]:
    """
    Request a withdrawal from AI wallet.
    
    - **withdraw_address**: Address to withdraw to
    - **amount**: Amount to withdraw (minimum: 50 USDT)
    """
    # Check minimum withdrawal amount
    if withdraw.amount < 50:
        raise HTTPException(status_code=400, detail="Minimum withdrawal amount is 50 USDT")
    
    # Get wallet
    wallet = await get_or_create_wallet(address)
    
    # Check balance
    if wallet["balance"] < withdraw.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # In a real system, this would initiate a withdrawal process
    # For this challenge, we'll just return a success message
    return {
        "message": "Withdrawal request submitted",
        "address": address,
        "withdraw_address": withdraw.withdraw_address,
        "amount": withdraw.amount
    }


# ===== Deposit & Withdrawal Endpoints =====

@router.get("/api/v1/deposits/wallet-address")
async def get_deposit_wallet_address(user_address: str) -> Dict[str, Any]:
    """
    获取用户的充值地址（如果不存在则自动创建）
    """
    from src.crypto.tron_chain import TronChainService
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT wallet_address FROM sub_wallets WHERE user_address = ?',
            (user_address,)
        )
        sub_wallet = await cursor.fetchone()
        
        if sub_wallet:
            # 已存在，直接返回
            return {
                "wallet_address": sub_wallet[0],
                "newly_created": False
            }
        
        # 不存在，自动创建（兼容老用户）
        tron_service = TronChainService()
        new_sub_wallet = tron_service.generate_sub_wallet()
        
        await db.execute('''
            INSERT INTO sub_wallets (user_address, wallet_address, private_key)
            VALUES (?, ?, ?)
        ''', (user_address, new_sub_wallet['address'], new_sub_wallet['private_key']))
        await db.commit()
        
        print(f"[Auto-Create] Sub-wallet created for user: {user_address}")
        
        return {
            "wallet_address": new_sub_wallet['address'],
            "newly_created": True
        }


@router.post("/api/v1/deposits/refresh-balance")
async def refresh_wallet_balance(refresh_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    刷新钱包余额 - 查询链上最新交易并更新数据库
    
    **Request Body:**
    ```json
    {
        "user_address": "0x123..."
    }
    ```
    """
    from src.crypto.tron_chain import TronChainService
    
    user_address = refresh_data.get('user_address')
    if not user_address:
        raise HTTPException(status_code=400, detail="Missing user_address")
    
    try:
        # 获取用户子钱包地址
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                'SELECT wallet_address FROM sub_wallets WHERE user_address = ?',
                (user_address,)
            )
            sub_wallet = await cursor.fetchone()
            
            if not sub_wallet:
                raise HTTPException(status_code=404, detail="Sub-wallet not found")
            
            wallet_address = sub_wallet[0]
        
        # 查询链上最新充值记录
        tron_service = TronChainService()
        deposits = tron_service.monitor_deposit(wallet_address, min_amount=0.01)
        
        if not deposits:
            return {
                "message": "No new deposits found",
                "balance_updated": False
            }
        
        # 处理新发现的交易
        new_deposits_count = 0
        total_new_amount = 0.0
        
        async with aiosqlite.connect(DB_PATH) as db:
            for dep in deposits:
                tx_hash = dep['tx_id']
                amount = dep['amount']
                
                # 检查是否已记录
                cursor = await db.execute(
                    'SELECT id FROM deposits WHERE tx_hash = ?',
                    (tx_hash,)
                )
                if await cursor.fetchone():
                    continue  # 已存在，跳过
                
                # 记录新充值
                deposit_id = await record_deposit(user_address, wallet_address, tx_hash, amount)
                
                # 自动确认
                await db.execute(
                    'UPDATE deposits SET status = ?, confirmed_at = ? WHERE id = ?',
                    ('confirmed', datetime.now().isoformat(), deposit_id)
                )
                
                # 更新人类钱包余额
                await db.execute(
                    'UPDATE human_wallets SET points_balance = points_balance + ?, total_deposited = total_deposited + ? WHERE address = ?',
                    (amount, amount, user_address)
                )
                
                new_deposits_count += 1
                total_new_amount += amount
            
            await db.commit()
        
        # 获取最新余额
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                'SELECT points_balance, total_deposited FROM human_wallets WHERE address = ?',
                (user_address,)
            )
            wallet = await cursor.fetchone()
        
        return {
            "message": f"Found {new_deposits_count} new deposit(s)",
            "new_deposits": new_deposits_count,
            "total_amount": total_new_amount,
            "balance_updated": new_deposits_count > 0,
            "wallet": {
                "points_balance": wallet[0] if wallet else 0,
                "total_deposited": wallet[1] if wallet else 0
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Refresh Balance Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))
async def verify_deposit(verify_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证链上充值交易
    
    **Request Body:**
    ```json
    {
        "user_address": "0x123...",
        "tx_hash": "0xabc..."
    }
    ```
    """
    from src.crypto.tron_chain import TronChainService
    
    user_address = verify_data.get('user_address')
    tx_hash = verify_data.get('tx_hash')
    
    if not all([user_address, tx_hash]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    try:
        # 验证交易是否上链成功
        tron_service = TronChainService()
        tx_info = tron_service.verify_tx(tx_hash)
        
        if not tx_info.get('confirmed'):
            raise HTTPException(status_code=400, detail="Transaction not confirmed on chain")
        
        # 获取用户子钱包地址
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                'SELECT wallet_address FROM sub_wallets WHERE user_address = ?',
                (user_address,)
            )
            sub_wallet = await cursor.fetchone()
            
            if not sub_wallet:
                raise HTTPException(status_code=404, detail="Sub-wallet not found")
            
            wallet_address = sub_wallet[0]
            
            # 检查该交易哈希是否已经记录
            cursor = await db.execute(
                'SELECT id FROM deposits WHERE tx_hash = ?',
                (tx_hash,)
            )
            if await cursor.fetchone():
                raise HTTPException(status_code=409, detail="This transaction has already been recorded")
        
        # 从链上查询实际到账金额
        deposits = tron_service.monitor_deposit(wallet_address, min_amount=0.01)
        actual_amount = 0.0
        
        for dep in deposits:
            if dep['tx_id'] == tx_hash:
                actual_amount = dep['amount']
                break
        
        if actual_amount == 0.0:
            # 尝试直接查询余额变化
            actual_amount = tron_service.get_balance(wallet_address)
        
        # 记录充值
        async with aiosqlite.connect(DB_PATH) as db:
            deposit_id = await record_deposit(user_address, wallet_address, tx_hash, actual_amount)
            
            # 自动确认并更新余额
            await db.execute(
                'UPDATE deposits SET status = ?, confirmed_at = ? WHERE id = ?',
                ('confirmed', datetime.now().isoformat(), deposit_id)
            )
            
            # 更新人类钱包余额
            await db.execute(
                'UPDATE human_wallets SET points_balance = points_balance + ?, total_deposited = total_deposited + ? WHERE address = ?',
                (actual_amount, actual_amount, user_address)
            )
            
            await db.commit()
        
        return {
            "message": "Deposit confirmed from on-chain transaction",
            "deposit_id": deposit_id,
            "amount": actual_amount,
            "tx_hash": tx_hash,
            "status": "confirmed"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/admin/deposits/manual")
async def admin_manual_deposit(deposit_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    管理员手动充值（测试用）
    
    **Request Body:**
    ```json
    {
        "user_address": "AI钱包地址",
        "amount": 100.0,
        "reason": "测试充值"
    }
    ```
    """
    user_address = deposit_data.get('user_address')
    amount = deposit_data.get('amount')
    reason = deposit_data.get('reason', 'Manual deposit')
    
    if not all([user_address, amount]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Update both users.ai_balance and ai_wallets.balance
        await db.execute(
            'UPDATE users SET ai_balance = ai_balance + ? WHERE ai_address = ?',
            (amount, user_address)
        )
        
        await db.execute(
            'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
            (amount, user_address)
        )
        
        # Check if update successful
        if db.total_changes == 0:
            raise HTTPException(status_code=404, detail="AI wallet not found")
        
        await db.commit()
        
        print(f"[Admin Deposit] {amount} USDT added to AI wallet: {user_address}")
    
    return {
        "message": "Deposit successful",
        "amount": amount,
        "ai_wallet_address": user_address
    }


@router.post("/api/v1/admin/deposits/batch")
async def admin_batch_deposit(batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    管理员批量充值（用于 AI 多层销售测试）
    
    **Request Body:**
    ```json
    {
        "deposits": [
            {"user_address": "0x123...", "amount": 100.0, "reason": "测试充值"},
            {"user_address": "0x456...", "amount": 200.0, "reason": "AI销售奖励"}
        ]
    }
    ```
    """
    deposits_list = batch_data.get('deposits', [])
    
    if not deposits_list:
        raise HTTPException(status_code=400, detail="No deposits provided")
    
    results = []
    failed = []
    
    async with aiosqlite.connect(DB_PATH) as db:
        for item in deposits_list:
            try:
                user_address = item.get('user_address')
                amount = item.get('amount')
                reason = item.get('reason', 'Batch deposit')
                
                if not all([user_address, amount]) or amount <= 0:
                    failed.append({"user_address": user_address, "error": "Invalid data"})
                    continue
                
                # 检查用户是否存在 - 支持 Tron 子钱包地址
                cursor = await db.execute(
                    'SELECT id FROM users WHERE address = ?',
                    (user_address,)
                )
                user_row = await cursor.fetchone()
                target_address = user_address
                
                if not user_row:
                    cursor = await db.execute(
                        'SELECT user_address FROM sub_wallets WHERE wallet_address = ?',
                        (user_address,)
                    )
                    sub_row = await cursor.fetchone()
                    if not sub_row:
                        failed.append({"user_address": user_address, "error": "User not found"})
                        continue
                    target_address = sub_row[0]
                
                # 记录充值
                deposit_id = await record_deposit(
                    user_address=target_address,
                    wallet_address='ADMIN_BATCH',
                    tx_hash=f'BATCH_{datetime.now().strftime("%Y%m%d%H%M%S")}_{target_address[:8]}',
                    amount=amount
                )
                
                # 自动确认
                await db.execute(
                    'UPDATE deposits SET status = ?, confirmed_at = ?, notes = ? WHERE id = ?',
                    ('confirmed', datetime.now().isoformat(), reason, deposit_id)
                )
                
                # 更新余额
                await db.execute(
                    'UPDATE human_wallets SET points_balance = points_balance + ?, total_deposited = total_deposited + ? WHERE address = ?',
                    (amount, amount, target_address)
                )
                
                results.append({
                    "user_address": user_address,
                    "amount": amount,
                    "deposit_id": deposit_id,
                    "status": "success"
                })
            except Exception as e:
                failed.append({"user_address": item.get('user_address'), "error": str(e)})
        
        await db.commit()
    
    return {
        "message": f"Batch deposit completed: {len(results)} success, {len(failed)} failed",
        "successful": results,
        "failed": failed,
        "total_amount": sum(r['amount'] for r in results)
    }


@router.get("/api/v1/admin/deposits")
async def list_pending_deposits() -> Dict[str, Any]:
    """
    List all deposits for admin review.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM deposits ORDER BY created_at DESC LIMIT 100'
        )
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        deposits = [dict(zip(columns, row)) for row in rows]
    
    return {"deposits": deposits, "total": len(deposits)}


@router.post("/api/v1/withdrawals")
async def create_withdrawal(withdraw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Request a withdrawal (will be processed by admin).
    
    **Request Body:**
    ```json
    {
        "user_address": "0x123...",
        "amount": 50.0,
        "withdraw_address": "0x456..."
    }
    ```
    """
    user_address = withdraw_data.get('user_address')
    amount = withdraw_data.get('amount')
    withdraw_address = withdraw_data.get('withdraw_address', user_address)
    
    if not all([user_address, amount]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Check minimum withdrawal
    if amount < 50:
        raise HTTPException(status_code=400, detail="Minimum withdrawal is 50 USDT")
    
    # Get human wallet
    wallet = await get_or_create_human_wallet(user_address)
    
    # Check balance
    if wallet['points_balance'] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Record withdrawal
    withdrawal_id = await record_withdrawal(user_address, amount)
    
    # In production, this would trigger actual blockchain transfer
    # For now, mark as completed immediately
    await complete_withdrawal(withdrawal_id, f"0x_simulated_tx_{withdrawal_id}")
    
    return {
        "message": "Withdrawal processed",
        "withdrawal_id": withdrawal_id,
        "amount": amount,
        "status": "completed"
    }


# ===== User Authentication Endpoints =====


@router.post("/api/v1/users/register")
async def user_register(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 1: Register with email, generate verification code.
    """
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    referrer_address = data.get('referrer_address') or ''
    if isinstance(referrer_address, str):
        referrer_address = referrer_address.strip()
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check if email already registered
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        )
        existing = await cursor.fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate 6-digit verification code
        code = ''.join(random.choices(string.digits, k=6))
        expires = datetime.now() + timedelta(minutes=10)
        
        # Store temp user data (will be activated after verification)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        await db.execute('''
            INSERT INTO users (email, password_hash, verification_code, verification_code_expires, is_verified)
            VALUES (?, ?, ?, ?, 0)
        ''', (email, password_hash, code, expires.isoformat()))
        await db.commit()
        
    # TODO: Send email with code in production
    # For now, return code in response for development
    return {
        "message": "Verification code sent to email",
        "mockCode": code,  # Remove in production
        "email": email,
        "referrer_address": referrer_address  # Pass to verify step
    }


@router.post("/api/v1/users/verify-email")
async def user_verify_email(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 2: Verify email code and activate account.
    Creates user wallets after verification.
    """
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    referrer_address = data.get('referrer_address') or ''
    if isinstance(referrer_address, str):
        referrer_address = referrer_address.strip()
    
    if not email or not code:
        raise HTTPException(status_code=400, detail="Email and code are required")
    
    # If no referrer, use platform master wallet as default referrer
    if not referrer_address:
        referrer_address = os.getenv('PLATFORM_WALLET_ADDRESS', '0x0000000000000000000000000000000000000000')
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Find pending registration
        cursor = await db.execute('''
            SELECT id, password_hash, verification_code, verification_code_expires, is_verified
            FROM users WHERE email = ?
        ''', (email,))
        user = await cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        if user['is_verified']:
            raise HTTPException(status_code=400, detail="Account already verified")
        
        if user['verification_code'] != code:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        expires = datetime.fromisoformat(user['verification_code_expires'])
        if datetime.now() > expires:
            raise HTTPException(status_code=400, detail="Verification code expired")
        
        # Activate account
        await db.execute('''
            UPDATE users SET is_verified = 1, verification_code = NULL, verification_code_expires = NULL
            WHERE email = ?
        ''', (email,))
            
        # Generate two Tron sub-wallets from master wallet
        from src.crypto.tron_chain import TronChainService
        tron_service = TronChainService()
        
        # Human wallet (for deposits and trading)
        human_sub_wallet = tron_service.generate_sub_wallet()
        human_address = human_sub_wallet['address']
        
        # AI wallet (for AI agent transactions and referral code)
        ai_sub_wallet = tron_service.generate_sub_wallet()
        ai_address = ai_sub_wallet['address']
        
        # Store addresses in users table
        await db.execute('''
            UPDATE users SET address = ?, ai_address = ?
            WHERE email = ?
        ''', (human_address, ai_address, email))
        
        # Store sub-wallets for reference
        await db.execute('''
            INSERT OR REPLACE INTO sub_wallets (user_address, wallet_address, private_key, wallet_type)
            VALUES (?, ?, ?, 'human')
        ''', (human_address, human_address, human_sub_wallet['private_key']))
        
        await db.execute('''
            INSERT OR REPLACE INTO sub_wallets (user_address, wallet_address, private_key, wallet_type)
            VALUES (?, ?, ?, 'ai')
        ''', (human_address, ai_address, ai_sub_wallet['private_key']))
        
        await db.commit()
        
        print(f"[Register] User {email} - Human: {human_address}, AI: {ai_address}")
    
    # Create AI wallet record
    ai_wallet = await get_or_create_wallet(ai_address)
    
    # Create human wallet record
    human_wallet = await get_or_create_human_wallet(human_address)
    
    # Record referral relationship if referrer provided
    if referrer_address:
        async with aiosqlite.connect(DB_PATH) as db:
            # Find referrer's user record by AI address
            cursor = await db.execute(
                'SELECT address, ai_address, tu1, tu2 FROM users WHERE ai_address = ?',
                (referrer_address,)
            )
            referrer = await cursor.fetchone()
            
            if referrer:
                referrer_human_addr = referrer[0]
                referrer_ai_addr = referrer[1]
                referrer_tu1 = referrer[2]  # Referrer's level 1
                referrer_tu2 = referrer[3]  # Referrer's level 2
                
                # Set new user's referral chain
                # Level 1: The direct referrer (their AI address)
                # Level 2: Referrer's level 1 (their AI address)
                # Level 3: Referrer's level 2 (their AI address)
                
                new_tu1 = referrer_ai_addr
                new_tu2 = referrer_tu1
                new_tu3 = referrer_tu2
                
                await db.execute(
                    'UPDATE users SET tu1 = ?, tu2 = ?, tu3 = ? WHERE address = ?',
                    (new_tu1, new_tu2, new_tu3, human_address)
                )
                await db.commit()
                
                print(f"[Referral] New user {human_address} - tu1:{new_tu1}, tu2:{new_tu2}, tu3:{new_tu3}")
    
    # Generate mock JWT token
    token = hashlib.sha256(f"{email}_{datetime.now().isoformat()}".encode()).hexdigest()
    
    return {
        "message": "Registration successful",
        "token": token,
        "user": {
            "email": email,
            "address": human_address,
            "ai_wallet_address": ai_address,
            "reputation_score": 100
        }
    }


@router.post("/api/v1/users/login")
async def user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Login with email and password.
    """
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT id, email, address, reputation_score, is_verified
            FROM users WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        user = await cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user['is_verified']:
            raise HTTPException(status_code=400, detail="Account not verified")
        
        # Get AI wallet address from sub_wallets (within same connection)
        cursor = await db.execute(
            'SELECT wallet_address FROM sub_wallets WHERE user_address = ? AND wallet_type = ?',
            (user['address'], 'ai')
        )
        ai_row = await cursor.fetchone()
        ai_address = ai_row[0] if ai_row else None
    
    # Generate mock JWT token
    token = hashlib.sha256(f"{email}_{datetime.now().isoformat()}".encode()).hexdigest()
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "email": user['email'],
            "address": user['address'],
            "ai_wallet_address": ai_address,
            "reputation_score": user['reputation_score']
        }
    }


@router.post("/api/v1/users/third-party-login")
async def user_third_party_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Third-party login (Google, GitHub, etc.) - Mock implementation.
    """
    provider = data.get('provider', '')
    provider_id = data.get('providerId', '')
    email = data.get('email', '').strip().lower()
    name = data.get('name', '')
    
    if not email or not provider:
        raise HTTPException(status_code=400, detail="Email and provider are required")
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Check if user exists
        cursor = await db.execute('''
            SELECT id, email, address, reputation_score, is_verified
            FROM users WHERE email = ?
        ''', (email,))
        user = await cursor.fetchone()
    
    if not user:
        # Auto-create account for third-party login
        password_hash = hashlib.sha256(f"oauth_{provider}_{provider_id}".encode()).hexdigest()
        import nacl.signing
        seed = hashlib.sha256(f"{email}_oauth_seed".encode()).digest()[:32]
        signing_key = nacl.signing.SigningKey(seed)
        verify_key = signing_key.verify_key
        address = '0x' + verify_key.encode().hex()[:40]
        
        await db.execute('''
            INSERT INTO users (email, password_hash, address, name, is_verified)
            VALUES (?, ?, ?, ?, 1)
        ''', (email, password_hash, address, name))
        await db.commit()
            
        # Create wallets
        await get_or_create_wallet(address)
        await get_or_create_human_wallet(address)
        
        user = {
            'email': email,
            'address': address,
            'reputation_score': 100
        }
    
    token = hashlib.sha256(f"{email}_{datetime.now().isoformat()}".encode()).hexdigest()
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "email": user['email'],
            "address": user['address'],
            "reputation_score": user['reputation_score']
        }
    }


# ===== Referral System Endpoints =====


@router.post("/api/v1/register")
async def register_user(register_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a new user with optional referrer.
    """
    user_address = register_data.get('address')
    referrer_address = register_data.get('referrer_address')
    
    if not user_address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    # Create human wallet
    wallet = await get_or_create_human_wallet(user_address)
    
    # Create AI wallet
    ai_wallet = await get_or_create_wallet(user_address)
    
    # Record referral relationship if referrer provided
    if referrer_address:
        await add_referral_relationship(user_address, referrer_address, level=1)
    
    return {
        "message": "User registered successfully",
        "address": user_address,
        "has_referrer": referrer_address is not None
    }


@router.get("/api/v1/referrals/{address}", response_model=ReferralResponse)
async def get_referrals(address: str) -> ReferralResponse:
    """
    Get referral relationships for an address.
    """
    # In a real system, this would return the actual referral chain
    # For this challenge, we'll return a placeholder
    return ReferralResponse(
        address=address,
        referrals=[]
    )

@router.get("/api/v1/referrals/records")
async def get_referral_records(limit: int = Query(50, ge=1, le=100)) -> Dict[str, Any]:
    """
    Get recent referral settlement records.
    Useful for debugging and auditing commission flows.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM transaction_referrals ORDER BY id DESC LIMIT ?',
            (limit,)
        )
        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        records = [dict(zip(columns, row)) for row in rows]
    
    return {"records": records, "total": len(records)}

@router.get("/api/v1/users/referral-network")
async def get_user_referral_network() -> Dict[str, Any]:
    """
    Get all users and their referral relationships.
    Shows who referred whom (tu1, tu2, tu3 chain).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Get all users with referral info
        cursor = await db.execute(
            'SELECT address, email, tu1, tu2, tu3 FROM users'
        )
        users = await cursor.fetchall()
        
        result = []
        for u in users:
            result.append({
                "address": u[0],
                "email": u[1],
                "tu1": u[2],  # First-level referrer
                "tu2": u[3],  # Second-level referrer
                "tu3": u[4]   # Third-level referrer
            })
        
        return {"users": result, "total": len(result)}


# ============================================
# Product Management APIs
# ============================================

class ProductSpecs(BaseModel):
    runtime: str = ""
    delivery_type: str = "source_code" # source_code, executable, dataset, api_key
    format: str = ""
    volume: str = ""
    metrics: Dict[str, Any] = {}

class ProductCreate(BaseModel):
    seller_address: str
    name: str
    description: str
    price: float
    currency: str = "TRX"
    category_id: str
    delivery_hash: str
    specs: ProductSpecs = ProductSpecs()

class ProductResponse(BaseModel):
    product_id: str
    seller_address: str
    name: str
    description: str
    price: float
    currency: str
    category_id: str
    specs: Dict[str, Any]
    delivery_hash: str
    contract_hash: str
    status: str
    created_at: str


@router.post("/api/v1/products", response_model=Dict[str, Any])
async def create_new_product(product: ProductCreate) -> Dict[str, Any]:
    """
    Create a new micro-transaction product listing (AI-Native).
    """
    print(f"[DEBUG] 收到微交易发布请求: {product.name}, seller={product.seller_address}")
    try:
        # Validate seller exists
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('SELECT address FROM users WHERE address = ?', (product.seller_address,))
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code=400,
                    detail=f"Seller address {product.seller_address} is not registered."
                )
        
        # Prepare data for DB (convert Pydantic model to dict)
        product_data = product.dict()
        
        # Create product in database (Contract Hash is generated inside create_product)
        product_id = await create_product(product_data)
        
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product listed successfully. Contract hash will be anchored in next batch."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to create product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/products")
async def get_products_list(
    status: str = Query("active", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """
    List all active products with pagination.
    """
    try:
        products = await list_products(status=status, limit=limit, offset=offset)
        
        return {
            "products": products,
            "total": len(products),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/products/{product_id}")
async def get_product_details(product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.
    """
    product = await get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"product": product}


# ============================================
# Contract Management APIs
# ============================================

class ContractCreate(BaseModel):
    product_id: str
    buyer_address: str
    seller_address: str
    contract_hash: str
    file_hash: str = ""


class ContractAnchorUpdate(BaseModel):
    github_url: str
    commit_sha: str


@router.post("/api/v1/contracts", response_model=Dict[str, Any])
async def create_new_contract(contract: ContractCreate) -> Dict[str, Any]:
    """
    Create a new contract when a transaction is initiated.
    """
    try:
        # Verify product exists
        product = await get_product(contract.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create contract
        contract_data = contract.dict()
        contract_id = await create_contract(contract_data)
        
        return {
            "message": "Contract created successfully",
            "contract_id": contract_id,
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/contracts/{contract_id}/anchor")
async def update_contract_anchor_info(
    contract_id: str,
    anchor_data: ContractAnchorUpdate
) -> Dict[str, Any]:
    """
    Update contract with GitHub anchor information.
    """
    contract = await get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    success = await update_contract_anchor(
        contract_id,
        anchor_data.github_url,
        anchor_data.commit_sha
    )
    
    if success:
        return {
            "message": "Contract anchor updated",
            "github_url": anchor_data.github_url,
            "commit_sha": anchor_data.commit_sha
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update anchor")


@router.post("/api/v1/contracts/{contract_id}/status")
async def update_contract_status_endpoint(
    contract_id: str,
    status_data: Dict[str, str]
) -> Dict[str, Any]:
    """
    Update contract status (completed, cancelled, disputed).
    """
    contract = await get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    new_status = status_data.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    valid_statuses = ['created', 'active', 'completed', 'cancelled', 'disputed']
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    success = await update_contract_status(contract_id, new_status)
    
    if success:
        return {
            "message": f"Contract status updated to {new_status}",
            "contract_id": contract_id,
            "status": new_status
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update status")


@router.get("/api/v1/contracts/{contract_id}")
async def get_contract_details(contract_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific contract.
    """
    contract = await get_contract(contract_id)
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    return {"contract": contract}


# ============================================
# Arbitration APIs
# ============================================

class DisputeCreate(BaseModel):
    contract_id: str
    dispute_type: str
    description: str
    evidence: List[Dict[str, Any]] = []


class EvidenceSubmit(BaseModel):
    evidence: List[Dict[str, Any]]


@router.post("/api/v1/arbitration/dispute", response_model=Dict[str, Any])
async def create_dispute(dispute_data: DisputeCreate) -> Dict[str, Any]:
    """
    Initiate a new dispute for a contract.
    
    - **contract_id**: The contract being disputed
    - **dispute_type**: Type of dispute (functionality, delivery, quality, etc.)
    - **description**: Detailed description
    - **evidence**: Evidence submitted by complainant
    """
    try:
        # Verify contract exists
        contract = await get_contract(dispute_data.contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Get buyer and seller addresses from contract
        complainant = contract.get('buyer_address', '')
        respondent = contract.get('seller_address', '')
        
        # Initiate dispute in arbitration engine
        dispute = await arbitration_engine.initiate_dispute(
            contract_id=dispute_data.contract_id,
            dispute_type=dispute_data.dispute_type,
            complainant_address=complainant,
            respondent_address=respondent,
            description=dispute_data.description,
            evidence=dispute_data.evidence
        )
        
        # Update contract status to disputed
        await update_contract_status(dispute_data.contract_id, 'disputed')
        
        return {
            "message": "Dispute initiated successfully",
            "dispute_id": dispute["dispute_id"],
            "status": dispute["status"],
            "deadline": dispute["deadline"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/arbitration/{dispute_id}/evidence")
async def submit_evidence(
    dispute_id: str,
    evidence_data: EvidenceSubmit
) -> Dict[str, Any]:
    """
    Submit evidence from respondent (seller).
    """
    try:
        dispute = await arbitration_engine.get_dispute_status(dispute_id)
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
        
        success = await arbitration_engine.submit_respondent_evidence(
            dispute_id,
            evidence_data.evidence
        )
        
        if success:
            return {
                "message": "Evidence submitted successfully",
                "dispute_id": dispute_id,
                "status": "Evidence received, validation in progress"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit evidence")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/arbitration/{dispute_id}")
async def get_dispute_status(dispute_id: str) -> Dict[str, Any]:
    """
    Get current status of a dispute.
    """
    dispute = await arbitration_engine.get_dispute_status(dispute_id)
    
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    return {"dispute": dispute}


@router.get("/api/v1/arbitration/list")
async def list_disputes(status: str = None) -> Dict[str, Any]:
    """
    List all disputes, optionally filtered by status.
    """
    disputes = await arbitration_engine.list_disputes(status)
    
    return {
        "disputes": disputes,
        "total": len(disputes)
    }


# ============================================
# Core Protocol Algorithm APIs
# These are the foundational algorithms of Black2 Clearing Protocol
# Can be used independently by any application
# ============================================

# --- Cryptography & Identity APIs ---

class KeyGenRequest(BaseModel):
    pass

class KeyGenResponse(BaseModel):
    private_key: str
    public_key: str
    did: str  # Decentralized Identifier

class SignRequest(BaseModel):
    private_key: str
    message: str

class SignResponse(BaseModel):
    signature: str

class VerifyRequest(BaseModel):
    public_key: str
    message: str
    signature: str

class VerifyResponse(BaseModel):
    valid: bool
    message: str

class HashRequest(BaseModel):
    data: Any


class HashResponse(BaseModel):
    hash: str


@router.post("/api/v1/crypto/keygen", response_model=KeyGenResponse)
async def generate_keys(request: KeyGenRequest = None) -> KeyGenResponse:
    """
    Generate Ed25519 key pair and DID.
    
    This is the foundation of identity in Black2 Protocol.
    Returns private key, public key, and decentralized identifier (DID).
    
    **Use Cases:**
    - User registration
    - AI agent identity creation
    - Wallet generation
    """
    keys = generate_keypair()
    
    # Generate DID from public key
    import base58
    did = f"did:black2:{base58.b58encode(bytes.fromhex(keys['public_key'])).decode()}"
    
    return KeyGenResponse(
        private_key=keys['private_key'],
        public_key=keys['public_key'],
        did=did
    )


@router.post("/api/v1/crypto/sign", response_model=SignResponse)
async def sign_data(request: SignRequest) -> SignResponse:
    """
    Sign any data with Ed25519 private key.
    
    **Use Cases:**
    - Transaction signing
    - Contract approval
    - Message authentication
    """
    signature = sign_message(request.private_key, request.message)
    return SignResponse(signature=signature)


@router.post("/api/v1/crypto/verify", response_model=VerifyResponse)
async def verify_signature_api(request: VerifyRequest) -> VerifyResponse:
    """
    Verify an Ed25519 signature.
    
    **Use Cases:**
    - Transaction verification
    - Identity authentication
    - Data integrity check
    """
    is_valid = verify_signature(request.public_key, request.message, request.signature)
    
    return VerifyResponse(
        valid=is_valid,
        message="Signature valid" if is_valid else "Invalid signature"
    )


@router.post("/api/v1/crypto/hash", response_model=HashResponse)
async def compute_hash(request: HashRequest) -> HashResponse:
    """
    Compute SHA-256 hash of any data.
    
    **Use Cases:**
    - File integrity verification
    - Contract hash generation
    - Data fingerprinting
    """
    hash_value = sha256_hash(request.data)
    return HashResponse(hash=hash_value)


# --- Contract Template APIs ---

@router.get("/api/v1/protocol/templates")
async def get_all_templates() -> Dict[str, Any]:
    """
    List all standardized contract templates.
    
    Returns template IDs, names, and versions.
    Use `/api/v1/protocol/templates/{template_id}` for full details.
    """
    templates = list_templates()
    return {"templates": templates, "total": len(templates)}


@router.get("/api/v1/protocol/templates/{template_id}")
async def get_template_detail(template_id: str) -> Dict[str, Any]:
    """
    Get detailed contract template structure.
    
    Returns field definitions, required fields, validation rules.
    """
    print(f"[DEBUG] 请求模板详情: {template_id}")
    try:
        template = get_template(template_id)
        print(f"[DEBUG] 模板找到: {template.get('name')}")
        return {"template": template}
    except ValueError as e:
        print(f"[ERROR] 模板未找到: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"[ERROR] 模板加载异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/protocol/contract-hash")
async def compute_contract_hash(contract_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate contract hash from contract data.
    
    Following Black2 Protocol Section 2.7 Rule 1:
    Contract Hash = SHA256(all contract terms + file_hash + seller_id + timestamp)
    
    **Use Cases:**
    - Contract creation
    - Contract integrity verification
    - GitHub anchoring preparation
    """
    contract_hash = generate_contract_hash(contract_data)
    return {
        "contract_hash": contract_hash,
        "algorithm": "SHA-256",
        "input_fields": list(contract_data.keys())
    }


@router.post("/api/v1/protocol/validate-contract")
async def validate_contract(validation_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate contract data against template requirements.
    
    **Request Body:**
    ```json
    {
        "template_id": "TPL_SOFTWARE_001",
        "contract_data": {...}
    }
    ```
    
    **Use Cases:**
    - Pre-submission validation
    - Form validation on frontend
    - Automated compliance checking
    """
    template_id = validation_request.get('template_id')
    contract_data = validation_request.get('contract_data', {})
    
    if not template_id:
        raise HTTPException(status_code=400, detail="template_id is required")
    
    result = validate_contract_against_template(template_id, contract_data)
    return result


@router.post("/api/v1/protocol/detect-effect-promise")
async def detect_effect_promise_api(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Detect effect promises in product description.
    
    Following Black2 Protocol Section 2.7 Rule 5:
    Effect promises result in automatic seller violation if disputed.
    
    **Request Body:**
    ```json
    {
        "description": "This tool can guarantee 10x profit..."
    }
    ```
    
    **Use Cases:**
    - Real-time warning during product listing
    - Automated compliance checking
    - Risk assessment
    """
    description = request.get('description', '')
    result = detect_effect_promise(description)
    return result


# --- Merkle Tree & Batch Anchoring APIs ---

class MerkleRootRequest(BaseModel):
    hashes: List[str]

class MerkleRootResponse(BaseModel):
    merkle_root: str
    algorithm: str
    input_count: int


@router.post("/api/v1/protocol/merkle-root", response_model=MerkleRootResponse)
async def calculate_merkle_root(request: MerkleRootRequest) -> MerkleRootResponse:
    """
    Calculate Merkle root from a list of transaction hashes.
    
    Following Black2 Protocol Section 2.5 for batch anchoring optimization.
    
    **Use Cases:**
    - Batch transaction anchoring
    - Reduced GitHub API calls
    - Efficient proof generation
    """
    anchor_service = GitHubAnchorService.__new__(GitHubAnchorService)
    merkle_root = anchor_service.calculate_merkle_root(request.hashes)
    
    return MerkleRootResponse(
        merkle_root=merkle_root,
        algorithm="SHA-256 Merkle Tree",
        input_count=len(request.hashes)
    )


# --- Reputation & Margin Calculation APIs ---

class ReputationCalcRequest(BaseModel):
    reputation_score: int
    price: float

class ReputationCalcResponse(BaseModel):
    reputation_score: int
    margin_percentage: float
    margin_amount: float
    can_publish: bool
    risk_level: str


@router.post("/api/v1/protocol/calculate-margin", response_model=ReputationCalcResponse)
async def calculate_margin(request: ReputationCalcRequest) -> ReputationCalcResponse:
    """
    Calculate margin percentage and amount based on reputation score.
    
    Following Black2 Protocol Section 2.8:
    - Score >= 90: 5% margin
    - Score >= 80: 10% margin
    - Score >= 70: 15% margin
    - Score >= 60: 20% margin
    - Score < 60: Cannot publish
    
    **Use Cases:**
    - Real-time margin calculation
    - Risk assessment
    - Pricing strategy
    """
    score = request.reputation_score
    price = request.price
    
    # Determine margin percentage
    if score >= 90:
        margin_pct = 5.0
        risk_level = "low"
    elif score >= 80:
        margin_pct = 10.0
        risk_level = "medium-low"
    elif score >= 70:
        margin_pct = 15.0
        risk_level = "medium"
    elif score >= 60:
        margin_pct = 20.0
        risk_level = "high"
    else:
        margin_pct = 0.0
        risk_level = "blocked"
    
    margin_amount = price * margin_pct / 100
    can_publish = score >= 60
    
    return ReputationCalcResponse(
        reputation_score=score,
        margin_percentage=margin_pct,
        margin_amount=round(margin_amount, 2),
        can_publish=can_publish,
        risk_level=risk_level
    )


# --- Referral Chain Calculation API ---

class ReferralChainRequest(BaseModel):
    buyer_address: str
    max_levels: int = 5

class ReferralChainResponse(BaseModel):
    chain: List[str]
    total_levels: int
    commission_rates: List[float]


@router.post("/api/v1/protocol/calculate-referral-chain", response_model=ReferralChainResponse)
async def calculate_referral_chain_api(request: ReferralChainRequest) -> ReferralChainResponse:
    """
    Calculate 5-level referral chain from buyer address.
    
    Following Black2 Protocol Section 2.6:
    Commission rates: [5%, 3%, 2%, 1%, 0.5%] = 11.5% total
    
    **Use Cases:**
    - Commission calculation
    - Reward distribution
    - Network analysis
    """
    chain = await calculate_referral_chain(request.buyer_address)
    
    # Standard commission rates for 5 levels
    commission_rates = [5.0, 3.0, 2.0, 1.0, 0.5]
    
    return ReferralChainResponse(
        chain=chain,
        total_levels=len(chain),
        commission_rates=commission_rates[:len(chain)]
    )


# --- Auto-Confirm Timer API ---

class AutoConfirmRequest(BaseModel):
    auto_confirm_hours: int
    transaction_timestamp: str

class AutoConfirmResponse(BaseModel):
    confirm_deadline: str
    hours_remaining: float
    is_expired: bool


@router.post("/api/v1/protocol/calculate-auto-confirm", response_model=AutoConfirmResponse)
async def calculate_auto_confirm(request: AutoConfirmRequest) -> AutoConfirmResponse:
    """
    Calculate auto-confirm deadline and remaining time.
    
    Following Black2 Protocol Section 2.4:
    - Minimum: 24 hours
    - Maximum: 168 hours (7 days)
    - Default: 72 hours
    
    **Use Cases:**
    - Countdown display
    - Automatic confirmation scheduling
    - Deadline monitoring
    """
    from datetime import datetime, timedelta
    
    # Validate hours
    hours = request.auto_confirm_hours
    if hours < 24 or hours > 168:
        raise HTTPException(
            status_code=400,
            detail="auto_confirm_hours must be between 24 and 168"
        )
    
    # Parse transaction timestamp
    try:
        tx_time = datetime.fromisoformat(request.transaction_timestamp.replace('Z', '+00:00'))
    except:
        tx_time = datetime.now(timezone.utc)
    
    # Calculate deadline
    deadline = tx_time + timedelta(hours=hours)
    now = datetime.now(timezone.utc)
    
    # Calculate remaining time
    remaining = (deadline - now).total_seconds() / 3600
    is_expired = remaining <= 0
    
    return AutoConfirmResponse(
        confirm_deadline=deadline.isoformat(),
        hours_remaining=max(0, round(remaining, 2)),
        is_expired=is_expired
    )


# --- Storage Plan Cost Calculation API ---

class StorageCostRequest(BaseModel):
    storage_plan: str  # "30days", "365days", "10years"
    file_size_mb: float = 10.0

class StorageCostResponse(BaseModel):
    plan: str
    duration_days: int
    cost_usd: float
    cost_per_day: float


@router.post("/api/v1/protocol/calculate-storage-cost", response_model=StorageCostResponse)
async def calculate_storage_cost(request: StorageCostRequest) -> StorageCostResponse:
    """
    Calculate storage cost based on plan and file size.
    
    Following Black2 Protocol Section 2.4:
    - 30 days: $0.5/month
    - 365 days: $4/year
    - 10 years: $30 one-time
    
    **Use Cases:**
    - Pricing display
    - Cost comparison
    - Budget planning
    """
    plan_costs = {
        "30days": {"days": 30, "cost": 0.5},
        "365days": {"days": 365, "cost": 4.0},
        "10years": {"days": 3650, "cost": 30.0}
    }
    
    if request.storage_plan not in plan_costs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid storage plan. Must be one of: {', '.join(plan_costs.keys())}"
        )
    
    plan_info = plan_costs[request.storage_plan]
    cost_per_day = plan_info["cost"] / plan_info["days"]
    
    return StorageCostResponse(
        plan=request.storage_plan,
        duration_days=plan_info["days"],
        cost_usd=plan_info["cost"],
        cost_per_day=round(cost_per_day, 4)
    )


# --- Protocol Version & Info API ---

@router.get("/api/v1/protocol/info")
async def get_protocol_info() -> Dict[str, Any]:
    """
    Get Black2 Clearing Protocol information.
    
    Returns protocol version, supported features, and capabilities.
    
    **Use Cases:**
    - Client compatibility check
    - Feature detection
    - System health check
    """
    return {
        "protocol_name": "Black2 Clearing Protocol",
        "version": "1.0.0",
        "description": "AI-to-AI Trusted Trading Infrastructure",
        "features": [
            "Ed25519 Identity & Signing",
            "SHA-256 Hash Anchoring",
            "GitHub Immutable Timestamping",
            "Merkle Tree Batch Optimization",
            "Standardized Contract Templates",
            "Effect Promise Detection",
            "5-Level Referral System",
            "Reputation-Based Margin",
            "Auto-Confirm Mechanism",
            "Automated Arbitration Engine"
        ],
        "endpoints": {
            "cryptography": "/api/v1/crypto/*",
            "contracts": "/api/v1/protocol/templates/*",
            "arbitration": "/api/v1/arbitration/*",
            "products": "/api/v1/products",
            "transactions": "/api/v1/transactions"
        },
        "documentation": "https://github.com/yongchaoqiu111/black2/docs/WHITEPAPER.md"
    }


# --- Sandbox Testing API ---

class SandboxTestRequest(BaseModel):
    dispute_id: str
    product_file: str
    contract_metrics: List[Dict[str, Any]]


class SandboxTestResponse(BaseModel):
    test_id: str
    overall_pass_rate: float
    metrics_tested: int
    execution_time_seconds: float
    environment: str


@router.post("/api/v1/arbitration/sandbox-test", response_model=SandboxTestResponse)
async def run_sandbox_test(request: SandboxTestRequest) -> SandboxTestResponse:
    """
    Execute automated sandbox tests for dispute resolution.
    
    Tests product functionality against quantifiable metrics defined in contract.
    Uses isolated environment (Docker if available, otherwise local).
    
    **Use Cases:**
    - Automated dispute resolution
    - Product quality verification
    - Performance benchmarking
    """
    try:
        # Execute sandbox tests
        test_results = await arbitration_engine.execute_sandbox_tests(
            dispute_id=request.dispute_id,
            product_file=request.product_file,
            contract_metrics=request.contract_metrics
        )
        
        return SandboxTestResponse(
            test_id=test_results["test_id"],
            overall_pass_rate=test_results["overall_pass_rate"],
            metrics_tested=test_results["metrics_tested"],
            execution_time_seconds=test_results["execution_time_seconds"],
            environment=test_results["environment"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/arbitration/{dispute_id}/test-report")
async def get_test_report(dispute_id: str) -> Dict[str, Any]:
    """
    Get human-readable test report for a dispute.
    
    Returns formatted test results with pass/fail status for each metric.
    """
    try:
        dispute = arbitration_engine.evidence_store.get(dispute_id)
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
        
        if "test_report" not in dispute:
            raise HTTPException(status_code=404, detail="Test report not available")
        
        return {
            "dispute_id": dispute_id,
            "report": dispute["test_report"],
            "test_results": dispute.get("test_results")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Merkle Batch Anchoring API ---

class BatchAnchorRequest(BaseModel):
    transaction_hashes: List[str]
    batch_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BatchAnchorResponse(BaseModel):
    batch_id: str
    merkle_root: str
    transaction_count: int
    commit_url: str
    anchor_timestamp: str
    proof_available: bool


class MerkleProofRequest(BaseModel):
    transaction_hash: str
    transaction_hashes: List[str]


class MerkleProofResponse(BaseModel):
    hash: str
    proof_path: List[Dict[str, Any]]
    merkle_root: str
    position: int
    total_transactions: int


class VerifyProofRequest(BaseModel):
    transaction_hash: str
    proof: Dict[str, Any]


class VerifyProofResponse(BaseModel):
    valid: bool
    message: str


@router.post("/api/v1/anchor/batch", response_model=BatchAnchorResponse)
async def anchor_batch(request: BatchAnchorRequest) -> BatchAnchorResponse:
    """
    Anchor multiple transaction hashes using Merkle root optimization.
    
    Following Black2 Protocol Section 4.3:
    - Calculate Merkle root from all transaction hashes
    - Submit single commit to GitHub with Merkle root and all hashes
    - Reduces GitHub API calls by ~90% for large batches
    
    **Use Cases:**
    - High-frequency trading platforms
    - Batch settlement systems
    - Cost optimization for anchoring
    
    **Example:**
    ```json
    {
        "transaction_hashes": ["hash1", "hash2", "hash3", "hash4"],
        "batch_id": "BATCH_20260421_001",
        "metadata": {"platform": "my_exchange"}
    }
    ```
    """
    if not github_anchor:
        raise HTTPException(
            status_code=503,
            detail="GitHub anchor service not configured (missing ANCHOR_GITHUB_TOKEN)"
        )
    
    if len(request.transaction_hashes) == 0:
        raise HTTPException(status_code=400, detail="At least one transaction hash required")
    
    try:
        result = await github_anchor.anchor_batch_transactions(
            transaction_hashes=request.transaction_hashes,
            batch_id=request.batch_id,
            metadata=request.metadata
        )
        
        return BatchAnchorResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/anchor/merkle-proof", response_model=MerkleProofResponse)
async def generate_merkle_proof(request: MerkleProofRequest) -> MerkleProofResponse:
    """
    Generate Merkle proof for a specific transaction in a batch.
    
    Allows verification that a transaction was included in a batch
    without revealing all other transactions.
    
    **Use Cases:**
    - Privacy-preserving verification
    - Selective disclosure
    - Audit trails
    """
    if not github_anchor:
        raise HTTPException(
            status_code=503,
            detail="GitHub anchor service not configured"
        )
    
    try:
        proof = github_anchor.generate_merkle_proof(
            transaction_hash=request.transaction_hash,
            transaction_hashes=request.transaction_hashes
        )
        
        return MerkleProofResponse(**proof)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/v1/anchor/verify-proof", response_model=VerifyProofResponse)
async def verify_merkle_proof(request: VerifyProofRequest) -> VerifyProofResponse:
    """
    Verify a Merkle proof.
    
    Confirms that a transaction hash is part of a batch
    by verifying the proof path against the Merkle root.
    
    **Use Cases:**
    - Transaction inclusion verification
    - Audit compliance
    - Dispute resolution
    """
    if not github_anchor:
        raise HTTPException(
            status_code=503,
            detail="GitHub anchor service not configured"
        )
    
    try:
        is_valid = github_anchor.verify_merkle_proof(
            transaction_hash=request.transaction_hash,
            proof=request.proof
        )
        
        return VerifyProofResponse(
            valid=is_valid,
            message="Proof verified successfully" if is_valid else "Invalid proof"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket Endpoints ====================

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time communication.
    
    Usage:
        ws://localhost:8080/ws/{user_id}
    
    Message format:
        {
            "type": "message_type",
            "data": {...}
        }
    """
    await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get('type')
            
            if message_type == 'ping':
                # Heartbeat
                await websocket.send_text(json.dumps({
                    'type': 'pong',
                    'timestamp': asyncio.get_event_loop().time()
                }))
            
            elif message_type == 'request_wallet_data':
                # 速率限制检查
                allowed, remaining = rate_limiter.is_allowed(f"wallet_{user_id}", interval=5)
                if not allowed:
                    await websocket.send_text(json.dumps({
                        'type': 'error',
                        'message': f'Rate limit exceeded. Try again in {remaining} seconds'
                    }))
                    continue
                
                # 生成并返回钱包数据（扁平化结构）
                ai_index = message.get('ai_index', 0)
                try:
                    wallet_info = hd_wallet_service.generate_ai_wallet(ai_index)
                    address = wallet_info['address']
                    
                    # 获取人类钱包
                    human_wallet = await get_or_create_human_wallet(address)
                    
                    # 获取 AI 钱包
                    ai_wallet = await get_or_create_wallet(address)
                    
                    # 查询推荐奖励（按层级分组）
                    db = await get_db()
                    rewards_result = await db.execute_fetchall('''
                        SELECT level, COUNT(*) as count, SUM(reward_amount) as total_amount
                        FROM referral_rewards
                        WHERE referrer_address = ?
                        GROUP BY level
                        ORDER BY level
                    ''', (address,))
                    
                    referral_rewards = [
                        {
                            'level': row['level'],
                            'count': row['count'],
                            'total_amount': row['total_amount'],
                            'currency': 'USDT'
                        }
                        for row in rewards_result
                    ]
                    
                    # 计算总收益
                    total_referral_earned = sum(r['total_amount'] for r in referral_rewards)
                    
                    await websocket.send_text(json.dumps({
                        'code': 200,
                        'success': True,
                        'data': {
                            'wallet': {
                                'address': address,
                                'balance_encrypted': True,
                                'total_earned': ai_wallet['total_earned'],
                                'currency': 'USDT'
                            },
                            'human_wallet': {
                                'points_balance': human_wallet['points_balance'],
                                'locked_points': human_wallet['locked_points'],
                                'total_deposited': human_wallet['total_deposited'],
                                'total_withdrawn': human_wallet['total_withdrawn'],
                                'currency': 'POINTS'
                            },
                            'referral_rewards': referral_rewards,
                            'total_referral_earned': total_referral_earned,
                            'team_stats': {
                                'total_referrals': ai_wallet['referral_count'],
                                'active_levels': len(referral_rewards)
                            }
                        },
                        'timestamp': int(asyncio.get_event_loop().time()),
                        'message': 'Success'
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        'code': 500,
                        'success': False,
                        'data': None,
                        'timestamp': int(asyncio.get_event_loop().time()),
                        'message': str(e)
                    }))
            
            elif message_type == 'join_room':
                # Join a room (e.g., chat room, transaction room)
                room_id = message.get('room_id')
                if room_id:
                    websocket_manager.join_room(user_id, room_id, websocket)
                    await websocket.send_text(json.dumps({
                        'type': 'room_joined',
                        'room_id': room_id
                    }))
            
            elif message_type == 'leave_room':
                # Leave a room
                room_id = message.get('room_id')
                if room_id:
                    websocket_manager.leave_room(user_id, room_id, websocket)
                    await websocket.send_text(json.dumps({
                        'type': 'room_left',
                        'room_id': room_id
                    }))
            
            else:
                # Unknown message type
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        websocket_manager.disconnect(user_id)
