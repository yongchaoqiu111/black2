"""
Black2 SDK - Complete Python Example

This example demonstrates:
1. Initializing B2P client and X402 bridge
2. Checking agent reputation
3. Creating a transaction with escrow payment
4. Handling disputes and arbitration
5. Releasing funds based on verdict

Requirements:
    pip install black2-sdk

Usage:
    python python_example.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from black2_sdk.black2 import B2PClient
from black2_sdk.black2.x402_bridge import X402Bridge, X402Error


def example_1_basic_initialization():
    """Example 1: Basic initialization of B2P SDK"""
    print("\n" + "="*60)
    print("Example 1: Basic Initialization")
    print("="*60)
    
    # Initialize B2P client in local mode
    client = B2PClient(local_mode=True)
    
    # Initialize X402 bridge in mock mode
    bridge = X402Bridge(mock_mode=True)
    
    print("✓ B2P Client initialized")
    print("✓ X402 Bridge initialized (mock mode)")
    
    return client, bridge


def example_2_check_agent_reputation(client):
    """Example 2: Check agent reputation and risk level"""
    print("\n" + "="*60)
    print("Example 2: Check Agent Reputation")
    print("="*60)
    
    # Check reputation for an AI agent
    agent_id = "agent_001"
    assessment = client.check_agent_risk(agent_id)
    
    print(f"Agent ID: {agent_id}")
    print(f"Risk Level: {assessment.get('risk_level', 'UNKNOWN')}")
    print(f"Friction Coefficient: {assessment.get('friction_coefficient', 'N/A')}")
    print(f"Total Score: {assessment.get('total_score', 'N/A')}")
    
    # Make decision based on risk level
    risk_level = assessment.get('risk_level', 'CRITICAL')
    if risk_level in ['LOW', 'MEDIUM']:
        print("✓ Agent is safe to transact with")
    else:
        print("⚠ Warning: High risk agent - proceed with caution")
    
    return assessment


def example_3_create_escrow_transaction(bridge):
    """Example 3: Create transaction with escrow payment"""
    print("\n" + "="*60)
    print("Example 3: Create Escrow Transaction")
    print("="*60)
    
    # Check buyer's balance first
    buyer_id = "buyer_001"
    balance = bridge.check_balance(buyer_id, "USDC")
    print(f"Buyer balance: {balance['balance']} {balance['asset']}")
    
    # Create escrow payment
    seller_id = "seller_002"
    amount = 500.0
    contract_hash = "abc123def456"  # Hash of agreed deliverables
    
    try:
        escrow_result = bridge.initiate_escrow_payment(
            sender_id=buyer_id,
            receiver_id=seller_id,
            amount=amount,
            asset="USDC",
            contract_hash=contract_hash
        )
        
        print(f"\n✓ Escrow created successfully!")
        print(f"Escrow ID: {escrow_result['escrow_id']}")
        print(f"Status: {escrow_result['status']}")
        print(f"Amount: {escrow_result['amount']} {escrow_result['asset']}")
        print(f"Message: {escrow_result['message']}")
        
        return escrow_result
        
    except X402Error as e:
        print(f"\n✗ Failed to create escrow: {e.message}")
        print(f"Error Code: {e.code.name}")
        return None


def example_4_simulate_delivery_and_dispute(bridge, escrow_result):
    """Example 4: Simulate delivery and dispute scenario"""
    print("\n" + "="*60)
    print("Example 4: Delivery and Dispute Simulation")
    print("="*60)
    
    if not escrow_result:
        print("✗ No escrow to process")
        return
    
    escrow_id = escrow_result['escrow_id']
    
    # Scenario A: Normal completion (seller delivers correct product)
    print("\n--- Scenario A: Normal Completion ---")
    delivered_hash = "abc123def456"  # Matches contract
    print(f"Seller delivers product with hash: {delivered_hash}")
    print("Contract hash matches delivered hash ✓")
    
    # Release funds to seller
    result = bridge.release_funds(
        escrow_id=escrow_id,
        recipient=escrow_result['receiver'],
        verdict="seller_wins"
    )
    print(f"Funds released to seller: {result['tx_hash']}")
    
    # Scenario B: Dispute (seller delivers wrong product)
    print("\n--- Scenario B: Quality Dispute ---")
    escrow_result2 = bridge.initiate_escrow_payment(
        sender_id="buyer_001",
        receiver_id="seller_003",
        amount=300.0,
        asset="USDC",
        contract_hash="contract_hash_123"
    )
    
    print(f"New escrow created: {escrow_result2['escrow_id']}")
    print("Seller delivers WRONG product (hash mismatch)")
    
    # In a real system, this would trigger a dispute via API
    # For now, we simulate the arbitration verdict
    print("Buyer initiates dispute...")
    print("Arbitration system compares hashes...")
    print("Verdict: buyer_wins (hash mismatch detected)")
    
    # Refund to buyer
    result2 = bridge.release_funds(
        escrow_id=escrow_result2['escrow_id'],
        recipient=escrow_result2['sender'],
        verdict="buyer_wins"
    )
    print(f"Funds refunded to buyer: {result2['tx_hash']}")


def example_5_error_handling(bridge):
    """Example 5: Error handling best practices"""
    print("\n" + "="*60)
    print("Example 5: Error Handling")
    print("="*60)
    
    # Try to check balance with invalid asset
    try:
        balance = bridge.check_balance("agent_001", "INVALID_TOKEN")
    except X402Error as e:
        print(f"\n✓ Caught expected error:")
        print(f"Code: {e.code.name}")
        print(f"Message: {e.message}")
    
    # Try to release funds for non-existent escrow
    try:
        result = bridge.release_funds(
            escrow_id="non_existent_escrow",
            recipient="someone",
            verdict="seller_wins"
        )
    except X402Error as e:
        print(f"\n✓ Caught expected error:")
        print(f"Code: {e.code.name}")
        print(f"Message: {e.message}")


def main():
    """Run all examples"""
    print("\n" + "#"*60)
    print("# Black2 SDK - Python Examples")
    print("#"*60)
    
    # Example 1: Initialization
    client, bridge = example_1_basic_initialization()
    
    # Example 2: Check reputation
    example_2_check_agent_reputation(client)
    
    # Example 3: Create escrow
    escrow_result = example_3_create_escrow_transaction(bridge)
    
    # Example 4: Delivery and dispute
    example_4_simulate_delivery_and_dispute(bridge, escrow_result)
    
    # Example 5: Error handling
    example_5_error_handling(bridge)
    
    print("\n" + "="*60)
    print("✓ All examples completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the documentation: README.md")
    print("2. Run the arbitration simulator: python test_arbitrator.py")
    print("3. Check JavaScript examples: javascript_example.js")


if __name__ == "__main__":
    main()
