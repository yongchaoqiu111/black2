"""
Black2 API Routes Module

Provides all API endpoints for transaction management, wallet operations, and referrals.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid

from src.db.transaction_db import (
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction_status,
    update_anchor_hash,
    get_or_create_wallet,
    add_referral_reward,
    calculate_referral_chain
)
from src.crypto.hash_service import sign_transaction, verify_transaction

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
    Create a new transaction.
    
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
    
    # Create transaction data
    tx_data = {
        "tx_id": tx_id,
        "from_address": transaction.from_address,
        "to_address": transaction.to_address,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "contract_hash": transaction.contract_hash,
        "file_hash": transaction.file_hash,
        "status": "pending",
        "referrer_address": transaction.referrer_address
    }
    
    # For demo purposes, use a dummy private key
    # In production, this would come from a secure key management system
    dummy_private_key = "0000000000000000000000000000000000000000000000000000000000000000"
    signed_tx = sign_transaction(tx_data, dummy_private_key)
    
    # Save to database
    created_tx = await create_transaction(signed_tx)
    
    # Handle referral rewards if referrer is provided
    if transaction.referrer_address:
        # Calculate referral chain (simplified)
        referral_chain = await calculate_referral_chain(transaction.from_address)
        
        # Add the direct referrer to the chain if not already there
        if transaction.referrer_address not in referral_chain:
            referral_chain.insert(0, transaction.referrer_address)
        
        # Limit to 5 levels
        referral_chain = referral_chain[:5]
        
        # Calculate and add rewards for each level
        reward_percentages = [0.05, 0.03, 0.02, 0.01, 0.005]  # 5%, 3%, 2%, 1%, 0.5%
        for i, referrer in enumerate(referral_chain):
            if i < len(reward_percentages):
                reward_amount = transaction.amount * reward_percentages[i]
                await add_referral_reward(tx_id, referrer, reward_amount, i + 1)
    
    return TransactionResponse(**created_tx)


@router.get("/api/v1/transactions/{tx_id}", response_model=TransactionResponse)
async def get_transaction_by_id(tx_id: str) -> TransactionResponse:
    """
    Get a transaction by its ID.
    """
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
    """
    List transactions with optional filters.
    
    - **status**: Filter by transaction status
    - **from_address**: Filter by sender address
    - **to_address**: Filter by recipient address
    - **limit**: Maximum number of transactions to return (default: 100)
    - **offset**: Offset for pagination (default: 0)
    """
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
async def update_transaction_status_endpoint(tx_id: str, update: TransactionStatusUpdate) -> Dict[str, bool]:
    """
    Update transaction status.
    
    - **status**: New status for the transaction
    - **file_hash**: Optional file hash to update
    """
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
    """
    Get AI wallet balance and details.
    """
    wallet = await get_or_create_wallet(address)
    return WalletResponse(**wallet)


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
