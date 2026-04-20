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
    get_contract
)
from src.crypto.hash_service import sign_transaction, verify_transaction, sha256_hash, generate_keypair, sign_message, verify_signature
from src.agents.arbitration_engine import arbitration_engine
from src.contract.templates import (
    get_template,
    list_templates,
    generate_contract_hash,
    validate_contract_against_template,
    detect_effect_promise
)
from src.anchor.github_anchor import GitHubAnchorService

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
        # Calculate referral chain (5 levels)
        referral_chain = await calculate_referral_chain(transaction.from_address)
        
        # Add the direct referrer to the chain if not already there
        if transaction.referrer_address not in referral_chain:
            referral_chain.insert(0, transaction.referrer_address)
        
        # Limit to 5 levels
        referral_chain = referral_chain[:5]
        
        # Calculate and add REWARDS AS PENDING (not distributed yet)
        reward_percentages = [0.05, 0.03, 0.02, 0.01, 0.005]  # 5%, 3%, 2%, 1%, 0.5%
        for i, referrer in enumerate(referral_chain):
            if i < len(reward_percentages):
                reward_amount = transaction.amount * reward_percentages[i]
                # Create pending reward record (will be settled after transaction completes)
                await add_referral_reward(tx_id, referrer, reward_amount, i + 1, status='pending')
    
    return TransactionResponse(**created_tx)


@router.post("/api/v1/transactions/{tx_id}/complete")
async def complete_transaction(tx_id: str) -> Dict[str, Any]:
    """
    Complete a transaction and settle referral rewards.
    Call this when buyer confirms receipt or auto-confirm timeout.
    """
    # Update transaction status
    await update_transaction_status(tx_id, 'completed')
    
    # Settle all pending referral rewards
    settled_count = await settle_referral_rewards(tx_id)
    
    return {
        "message": "Transaction completed",
        "tx_id": tx_id,
        "referral_rewards_settled": settled_count
    }


@router.post("/api/v1/transactions/{tx_id}/cancel")
async def cancel_transaction(tx_id: str) -> Dict[str, Any]:
    """
    Cancel a transaction and void referral rewards.
    """
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


# ===== Deposit & Withdrawal Endpoints =====

@router.post("/api/v1/deposit")
async def create_deposit(deposit_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Record a deposit transaction (after on-chain confirmation).
    """
    user_address = deposit_data.get('user_address')
    tx_hash = deposit_data.get('tx_hash')
    amount = deposit_data.get('amount')
    
    if not all([user_address, tx_hash, amount]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Record deposit
    deposit_id = await record_deposit(user_address, tx_hash, amount)
    
    # Confirm deposit and update balance
    success = await confirm_deposit(tx_hash)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to confirm deposit")
    
    return {
        "message": "Deposit confirmed",
        "deposit_id": deposit_id,
        "amount": amount
    }


@router.post("/api/v1/withdraw")
async def create_withdrawal(withdraw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Request a withdrawal (will be processed by admin).
    """
    user_address = withdraw_data.get('user_address')
    amount = withdraw_data.get('amount')
    gas_fee = withdraw_data.get('gas_fee', 0.0)
    
    if not all([user_address, amount]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Check user balance
    wallet = await get_or_create_human_wallet(user_address)
    if wallet['points_balance'] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Record withdrawal request
    withdrawal_id = await record_withdrawal(user_address, amount, gas_fee)
    
    return {
        "message": "Withdrawal request submitted",
        "withdrawal_id": withdrawal_id,
        "amount": amount,
        "status": "pending"
    }


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


# ============================================
# Product Management APIs
# ============================================

class ProductCreate(BaseModel):
    seller_address: str
    name: str
    description: str = ""
    price: float
    currency: str = "USD"
    category: str = ""
    version: str = ""
    system_requirements: str = ""
    contract_template: str = ""
    metrics: List[Dict[str, Any]] = []
    file_hash: str = ""
    delivery_method: str = ""
    auto_confirm_hours: int = 72
    storage_plan: str = ""
    delivery_checklist: Dict[str, bool] = {}
    reputation_score: int = 100
    margin_percentage: float = 5.0

class ProductResponse(BaseModel):
    product_id: str
    seller_address: str
    name: str
    description: str
    price: float
    currency: str
    category: str
    version: str
    system_requirements: str
    contract_template: str
    metrics: List[Dict[str, Any]]
    file_hash: str
    delivery_method: str
    auto_confirm_hours: int
    storage_plan: str
    delivery_checklist: Dict[str, bool]
    reputation_score: int
    margin_percentage: float
    status: str
    created_at: str


@router.post("/api/v1/products", response_model=Dict[str, Any])
async def create_new_product(product: ProductCreate) -> Dict[str, Any]:
    """
    Create a new product listing.
    
    - **seller_address**: Seller's wallet address
    - **name**: Product name
    - **price**: Product price
    - **metrics**: Quantifiable metrics array
    - **file_hash**: SHA-256 hash of product file
    """
    try:
        # Check reputation score
        if product.reputation_score < 60:
            raise HTTPException(
                status_code=403,
                detail="Reputation score too low to publish products (minimum 60)"
            )
        
        # Validate metrics
        if not product.metrics or len(product.metrics) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one quantifiable metric is required"
            )
        
        # Create product in database
        product_data = product.dict()
        product_id = await create_product(product_data)
        
        return {
            "message": "Product created successfully",
            "product_id": product_id,
            "status": "active"
        }
    except HTTPException:
        raise
    except Exception as e:
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
    try:
        template = get_template(template_id)
        return {"template": template}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
