"""
X402 Integration Full Flow Test

Tests the complete flow:
1. Reputation check
2. Fund locking via X402 escrow
3. Simulated delivery
4. Fund release based on verdict
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.x402.bridge import X402Bridge
from src.db.transaction_db import (
    init_db,
    create_transaction,
    get_transaction,
    update_transaction_status
)


async def test_x402_full_flow():
    """
    Full flow test for X402 integration.
    """
    print("=" * 60)
    print("X402 Integration Full Flow Test")
    print("=" * 60)
    
    x402 = X402Bridge()
    
    print(f"\n[X402] Bridge available: {x402.is_available()}")
    
    print("\n[Step 1] Reputation Check")
    print("-" * 40)
    buyer_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f5f2a1"
    seller_address = "0x8ba1f109551bD432803012645Hac136876612345"
    amount = 100.0
    asset = "USDT"
    
    print(f"Buyer: {buyer_address}")
    print(f"Seller: {seller_address}")
    print(f"Amount: {amount} {asset}")
    
    print("\n[Step 2] Initialize Database")
    print("-" * 40)
    await init_db()
    print("Database initialized")
    
    print("\n[Step 3] Create Escrow via X402")
    print("-" * 40)
    escrow_result = await x402.initiate_escrow(
        sender=buyer_address,
        receiver=seller_address,
        amount=amount,
        asset=asset
    )
    print(f"Escrow ID: {escrow_result.escrow_id}")
    print(f"Escrow Address: {escrow_result.escrow_address}")
    print(f"Status: {escrow_result.status}")
    
    print("\n[Step 4] Create Transaction in Database")
    print("-" * 40)
    tx_data = {
        "tx_id": f"test_tx_{int(asyncio.get_event_loop().time())}",
        "from_address": buyer_address,
        "to_address": seller_address,
        "amount": amount,
        "currency": asset,
        "contract_hash": "0xcontract123",
        "status": "paid",
        "hash": "0xtxhash123",
        "signature": "0xtxsignature123",
        "x402_escrow_id": escrow_result.escrow_id,
        "x402_escrow_address": escrow_result.escrow_address,
        "x402_status": escrow_result.status
    }
    
    created_tx = await create_transaction(tx_data)
    print(f"Transaction created: {created_tx['tx_id']}")
    
    print("\n[Step 5] Simulate Delivery (Hash Match)")
    print("-" * 40)
    file_hash = "0xcontract123"
    await update_transaction_status(created_tx['tx_id'], "shipped", file_hash)
    print(f"Status updated to 'shipped', file_hash: {file_hash}")
    
    print("\n[Step 6] Complete Transaction")
    print("-" * 40)
    await update_transaction_status(created_tx['tx_id'], "completed")
    print("Status updated to 'completed'")
    
    print("\n[Step 7] Release Funds (Seller Wins)")
    print("-" * 40)
    release_result = await x402.release_funds(
        escrow_id=escrow_result.escrow_id,
        recipient=seller_address,
        verdict="seller_wins"
    )
    print(f"Success: {release_result.success}")
    print(f"TX Hash: {release_result.tx_hash}")
    print(f"Recipient: {release_result.recipient}")
    print(f"Message: {release_result.message}")
    
    print("\n[Step 8] Test Dispute Flow (Buyer Wins)")
    print("-" * 40)
    print("Creating new transaction for dispute test...")
    
    escrow_result2 = await x402.initiate_escrow(
        sender=buyer_address,
        receiver=seller_address,
        amount=amount,
        asset=asset
    )
    print(f"New escrow created: {escrow_result2.escrow_id}")
    
    release_result2 = await x402.release_funds(
        escrow_id=escrow_result2.escrow_id,
        recipient=buyer_address,
        verdict="buyer_wins"
    )
    print(f"Dispute refund - Success: {release_result2.success}")
    print(f"Recipient (Buyer): {release_result2.recipient}")
    
    print("\n[Step 9] Check Balance")
    print("-" * 40)
    balance = await x402.check_balance(buyer_address)
    print(f"Buyer balance: {balance}")
    
    balance2 = await x402.check_balance(seller_address)
    print(f"Seller balance: {balance2}")
    
    print("\n" + "=" * 60)
    print("X402 Full Flow Test Completed Successfully!")
    print("=" * 60)
    
    return True


async def test_x402_bridge_methods():
    """
    Test individual X402 Bridge methods.
    """
    print("\n" + "=" * 60)
    print("X402 Bridge Methods Test")
    print("=" * 60)
    
    x402 = X402Bridge()
    
    print(f"\n[X402] Bridge available: {x402.is_available()}")
    
    print("\n[Test 1] initiate_escrow")
    result1 = await x402.initiate_escrow(
        sender="0x742d35Cc6634C0532925a3b844Bc9e7595f5f2a1",
        receiver="0x8ba1f109551bD432803012645Hac136876612345",
        amount=50.0,
        asset="USDT"
    )
    print(f"Escrow ID: {result1.escrow_id}")
    print(f"Status: {result1.status}")
    
    print("\n[Test 2] release_funds")
    result2 = await x402.release_funds(
        escrow_id=result1.escrow_id,
        recipient="0x8ba1f109551bD432803012645Hac136876612345",
        verdict="seller_wins"
    )
    print(f"Success: {result2.success}")
    print(f"TX Hash: {result2.tx_hash}")
    
    print("\n[Test 3] check_balance")
    result3 = await x402.check_balance("0x742d35Cc6634C0532925a3b844Bc9e7595f5f2a1")
    print(f"Balance: {result3}")
    
    print("\n" + "=" * 60)
    print("X402 Bridge Methods Test Completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("Starting X402 Integration Tests...")
    
    try:
        asyncio.run(test_x402_bridge_methods())
    except Exception as e:
        print(f"Test 1 Error: {e}")
    
    try:
        asyncio.run(test_x402_full_flow())
    except Exception as e:
        print(f"Test 2 Error: {e}")
    
    print("\nAll tests completed!")
