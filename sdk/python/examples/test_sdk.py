"""
Black2 SDK Test Script

This script demonstrates how AI agents can use the Black2 SDK to perform transactions.
Run this after starting the backend server (python server.py).
"""

import asyncio
import sys
import os

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

from black2_sdk import Black2Client, Black2APIError


async def test_sdk():
    """Test Black2 SDK functionality"""
    
    print("=" * 60)
    print("Black2 SDK Test - AI Agent Transaction Flow")
    print("=" * 60)
    
    # Initialize client
    api_base = os.getenv("BLACK2_API_BASE", "http://localhost:3000/api/v1")
    async with Black2Client(api_base=api_base) as client:
        
        try:
            # Step 1: Check seller reputation before trading
            print("\n[Step 1] Checking seller reputation...")
            seller_address = "0xSellerWalletAddress123"
            rep = await client.get_reputation(seller_address)
            print(f"✓ Seller reputation score: {rep['data'].get('reputation_score', 'N/A')}")
            
            # Step 2: Create a transaction (Escrow)
            print("\n[Step 2] Creating transaction (Escrow)...")
            buyer_address = "0xBuyerWalletAddress456"
            result = await client.create_transaction(
                from_address=buyer_address,
                to_address=seller_address,
                amount=50.0,
                contract_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA-256 of empty string
                currency="USDT"
            )
            tx_id = result['data']['tx_id']
            print(f"✓ Transaction created: {tx_id}")
            print(f"  Status: {result['data'].get('status')}")
            
            # Step 3: Get transaction details
            print("\n[Step 3] Fetching transaction details...")
            tx_details = await client.get_transaction(tx_id)
            print(f"✓ Amount: {tx_details['data'].get('amount')} USDT")
            print(f"  Escrow ID: {tx_details['data'].get('escrow_id')}")
            
            # Step 4: Complete transaction (triggers X402 fund release)
            print("\n[Step 4] Completing transaction (releasing funds)...")
            completion = await client.complete_transaction(tx_id)
            print(f"✓ {completion['message']}")
            if 'data' in completion and completion['data']:
                print(f"  Release TX Hash: {completion['data'].get('release_tx_hash', 'N/A')}")
            
            # Step 5: Check arbitration fund pool
            print("\n[Step 5] Checking arbitration fund pool...")
            pool = await client.get_arbitration_fund_pool()
            print(f"✓ Fund pool balance: {pool['data'].get('total_balance', 0)} USDT")
            print(f"  Total injections: {pool['data'].get('total_injections', 0)}")
            
            print("\n" + "=" * 60)
            print("All tests passed! ✓")
            print("=" * 60)
            
        except Black2APIError as e:
            print(f"\n✗ API Error [{e.code}]: {e.message}")
            if e.detail:
                print(f"  Detail: {e.detail}")
        except Exception as e:
            print(f"\n✗ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    api_base = os.getenv("BLACK2_API_BASE", "http://localhost:3000/api/v1")
    print(f"\nUsing API: {api_base}")
    asyncio.run(test_sdk())
