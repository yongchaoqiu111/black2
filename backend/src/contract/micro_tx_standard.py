"""
B2P Micro-Transaction Standard Definitions

Defines the atomic data structures and validation rules for high-frequency, 
low-value AI-to-AI transactions.
"""

from typing import Dict, Any, List, Optional
import hashlib
import json
import time
import uuid

# --- Data Structures (Schema) ---

MICRO_TX_SCHEMA = {
    "transaction_id": {"type": "string", "format": "uuid"},
    "asset_type": {
        "type": "string", 
        "enum": ["data_unit", "api_call", "compute_cycle", "token_access"]
    },
    "quantity": {"type": "number", "minimum": 0},
    "unit_price": {"type": "number", "minimum": 0},
    "total_amount": {"type": "number", "minimum": 0},
    "payload_hash": {"type": "string", "format": "sha256"},
    "execution_timestamp": {"type": "integer"},
    "settlement_mode": {
        "type": "string", 
        "enum": ["instant_x402", "batched_b2p"], 
        "default": "instant_x402"
    },
    "atomic_proof": {
        "type": "object",
        "properties": {
            "signature": {"type": "string"},
            "metadata": {"type": "object"}
        }
    }
}

# --- Methods (Logic) ---

def generate_micro_tx_id() -> str:
    """Generate a unique UUID for a micro-transaction."""
    return str(uuid.uuid4())

def calculate_payload_hash(payload: Any) -> str:
    """Calculate SHA-256 hash of the transaction payload."""
    if isinstance(payload, (dict, list)):
        content = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    else:
        content = str(payload)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def create_atomic_contract(
    asset_type: str,
    quantity: float,
    unit_price: float,
    payload: Any,
    seller_address: str,
    buyer_address: str
) -> Dict[str, Any]:
    """
    Create a standardized atomic micro-transaction contract.
    
    Args:
        asset_type: Type of digital asset (e.g., 'api_call').
        quantity: Amount of the asset.
        unit_price: Price per unit.
        payload: The actual data or service result being transacted.
        seller_address: Wallet address of the seller.
        buyer_address: Wallet address of the buyer.
        
    Returns:
        A dictionary representing the atomic contract.
    """
    tx_id = generate_micro_tx_id()
    total = round(quantity * unit_price, 8)
    p_hash = calculate_payload_hash(payload)
    timestamp = int(time.time())
    
    contract = {
        "template_id": "TPL_MICRO_001",
        "version": "1.0",
        "transaction_id": tx_id,
        "asset_type": asset_type,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": total,
        "payload_hash": p_hash,
        "execution_timestamp": timestamp,
        "seller_address": seller_address,
        "buyer_address": buyer_address,
        "settlement_mode": "instant_x402",
        "atomic_proof": {
            "signature": None, # To be signed by seller's wallet
            "metadata": {
                "created_at": timestamp,
                "protocol": "B2P-Micro-v1"
            }
        }
    }
    
    # Generate the final contract hash that will be anchored
    contract["contract_hash"] = generate_contract_hash(contract)
    return contract

def generate_contract_hash(contract_data: Dict[str, Any]) -> str:
    """Generate a deterministic hash for the contract terms."""
    # Exclude the hash field itself to prevent recursion
    data_to_hash = {k: v for k, v in contract_data.items() if k != "contract_hash"}
    normalized = json.dumps(data_to_hash, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def validate_micro_tx(contract: Dict[str, Any]) -> bool:
    """Validate the integrity of a micro-transaction contract."""
    required_fields = ["transaction_id", "asset_type", "total_amount", "payload_hash", "contract_hash"]
    for field in required_fields:
        if field not in contract:
            return False
    
    # Verify the hash
    expected_hash = generate_contract_hash(contract)
    return contract["contract_hash"] == expected_hash
