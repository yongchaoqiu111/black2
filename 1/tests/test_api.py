"""
Black2 API Tests

Unit tests for all API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_root():
    """
    Test root endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Black2 Clearing API"


def test_health_check():
    """
    Test health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_transaction():
    """
    Test creating a new transaction.
    """
    transaction_data = {
        "from_address": "0x1234567890123456789012345678901234567890",
        "to_address": "0x0987654321098765432109876543210987654321",
        "amount": 100.0,
        "currency": "USDT",
        "contract_hash": "0xhash123456",
        "file_hash": "0xfilehash123456",
        "referrer_address": "0xreferrer123456"
    }
    
    response = client.post("/api/v1/transactions", json=transaction_data)
    assert response.status_code == 200
    assert "tx_id" in response.json()
    assert response.json()["from_address"] == transaction_data["from_address"]
    assert response.json()["to_address"] == transaction_data["to_address"]
    assert response.json()["amount"] == transaction_data["amount"]


def test_get_transaction():
    """
    Test getting a transaction by ID.
    """
    # First create a transaction
    transaction_data = {
        "from_address": "0x1234567890123456789012345678901234567890",
        "to_address": "0x0987654321098765432109876543210987654321",
        "amount": 100.0,
        "currency": "USDT",
        "contract_hash": "0xhash123456"
    }
    
    create_response = client.post("/api/v1/transactions", json=transaction_data)
    tx_id = create_response.json()["tx_id"]
    
    # Then get the transaction
    get_response = client.get(f"/api/v1/transactions/{tx_id}")
    assert get_response.status_code == 200
    assert get_response.json()["tx_id"] == tx_id


def test_list_transactions():
    """
    Test listing transactions.
    """
    response = client.get("/api/v1/transactions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_verify_transaction():
    """
    Test verifying a transaction.
    """
    # First create a transaction
    transaction_data = {
        "from_address": "0x1234567890123456789012345678901234567890",
        "to_address": "0x0987654321098765432109876543210987654321",
        "amount": 100.0,
        "currency": "USDT",
        "contract_hash": "0xhash123456"
    }
    
    create_response = client.post("/api/v1/transactions", json=transaction_data)
    tx_id = create_response.json()["tx_id"]
    
    # Then verify the transaction (using dummy public key)
    verify_data = {
        "public_key": "0000000000000000000000000000000000000000000000000000000000000000"
    }
    
    verify_response = client.post(f"/api/v1/transactions/{tx_id}/verify", json=verify_data)
    assert verify_response.status_code == 200
    assert "valid" in verify_response.json()


def test_update_transaction_status():
    """
    Test updating transaction status.
    """
    # First create a transaction
    transaction_data = {
        "from_address": "0x1234567890123456789012345678901234567890",
        "to_address": "0x0987654321098765432109876543210987654321",
        "amount": 100.0,
        "currency": "USDT",
        "contract_hash": "0xhash123456"
    }
    
    create_response = client.post("/api/v1/transactions", json=transaction_data)
    tx_id = create_response.json()["tx_id"]
    
    # Then update the status
    update_data = {
        "status": "completed",
        "file_hash": "0xupdatedfilehash123456"
    }
    
    update_response = client.put(f"/api/v1/transactions/{tx_id}/status", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["updated"] == True


def test_get_wallet():
    """
    Test getting wallet information.
    """
    address = "0xwallet123456"
    response = client.get(f"/api/v1/wallet/{address}")
    assert response.status_code == 200
    assert response.json()["address"] == address
    assert "balance" in response.json()
    assert "total_earned" in response.json()
    assert "referral_count" in response.json()


def test_withdraw_from_wallet():
    """
    Test withdrawing from wallet.
    """
    address = "0xwallet123456"
    withdraw_data = {
        "withdraw_address": "0xwithdraw123456",
        "amount": 50.0
    }
    
    response = client.post(f"/api/v1/wallet/{address}/withdraw", json=withdraw_data)
    # Expect 400 because wallet balance is 0
    assert response.status_code == 400
    assert "detail" in response.json()


def test_get_referrals():
    """
    Test getting referral relationships.
    """
    address = "0xuser123456"
    response = client.get(f"/api/v1/referrals/{address}")
    assert response.status_code == 200
    assert response.json()["address"] == address
    assert "referrals" in response.json()
    assert isinstance(response.json()["referrals"], list)
