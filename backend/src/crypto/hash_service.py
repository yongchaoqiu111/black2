"""
Black2 Crypto Module - Hash and Signature Utilities

Provides:
- SHA-256 hashing for data integrity
- Ed25519 signing for identity verification
"""

import hashlib
import json
from typing import Any
import nacl.signing
from nacl.encoding import HexEncoder


def sha256_hash(data: Any) -> str:
    """
    Compute SHA-256 hash of any data.
    
    Args:
        data: Any serializable data (dict, list, str, etc.)
        
    Returns:
        Hex string of SHA-256 hash
    """
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
    
    return hashlib.sha256(data_bytes).hexdigest()


def generate_keypair() -> dict:
    """
    Generate Ed25519 key pair.
    
    Returns:
        Dict with 'private_key' and 'public_key' (hex encoded)
    """
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    
    return {
        'private_key': signing_key.encode(encoder=HexEncoder).decode('utf-8'),
        'public_key': verify_key.encode(encoder=HexEncoder).decode('utf-8')
    }


def sign_message(private_key_hex: str, message: str) -> str:
    """
    Sign a message with Ed25519 private key.
    
    Args:
        private_key_hex: Hex encoded private key
        message: Message to sign
        
    Returns:
        Hex encoded signature
    """
    signing_key = nacl.signing.SigningKey(private_key_hex.encode('utf-8'), encoder=HexEncoder)
    signed = signing_key.sign(message.encode('utf-8'))
    return signed.signature.hex()


def verify_signature(public_key_hex: str, message: str, signature_hex: str) -> bool:
    """
    Verify an Ed25519 signature.
    
    Args:
        public_key_hex: Hex encoded public key
        message: Original message
        signature_hex: Hex encoded signature
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        verify_key = nacl.signing.VerifyKey(public_key_hex.encode('utf-8'), encoder=HexEncoder)
        verify_key.verify(message.encode('utf-8'), bytes.fromhex(signature_hex))
        return True
    except Exception:
        return False


def sign_transaction(transaction: dict, private_key_hex: str) -> dict:
    """
    Sign a transaction and return it with signature.
    
    Args:
        transaction: Transaction dict
        private_key_hex: Hex encoded private key
        
    Returns:
        Transaction dict with added 'hash' and 'signature' fields
    """
    # Compute hash of transaction (excluding hash and signature fields)
    tx_data = {k: v for k, v in transaction.items() if k not in ['hash', 'signature']}
    tx_hash = sha256_hash(tx_data)
    
    # Sign the hash
    signature = sign_message(private_key_hex, tx_hash)
    
    return {
        **transaction,
        'hash': tx_hash,
        'signature': signature
    }


def verify_transaction(transaction: dict, public_key_hex: str) -> dict:
    """
    Verify a transaction's signature.
    
    Args:
        transaction: Transaction dict with 'hash' and 'signature'
        public_key_hex: Hex encoded public key
        
    Returns:
        Dict with 'valid' (bool) and 'message' (str)
    """
    if 'hash' not in transaction or 'signature' not in transaction:
        return {'valid': False, 'message': 'Missing hash or signature'}
    
    # Recompute hash
    tx_data = {k: v for k, v in transaction.items() if k not in ['hash', 'signature']}
    expected_hash = sha256_hash(tx_data)
    
    # Verify hash matches
    if transaction['hash'] != expected_hash:
        return {'valid': False, 'message': 'Hash mismatch - transaction tampered'}
    
    # Verify signature
    if not verify_signature(public_key_hex, transaction['hash'], transaction['signature']):
        return {'valid': False, 'message': 'Invalid signature'}
    
    return {'valid': True, 'message': 'Transaction verified'}
