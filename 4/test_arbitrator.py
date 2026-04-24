"""
Black2 Arbitration Simulator with X402 Payment Flow

This module provides a complete simulation of the B2P arbitration process,
including:
- Buyer complaint initiation
- Arbitrator voting and automated ruling
- X402 automatic refund/payment distribution
- Full transaction lifecycle testing

Usage:
    python test_arbitrator.py
    
Scenarios covered:
1. Normal completion (seller wins)
2. Product quality dispute (buyer wins)
3. Non-delivery dispute (buyer wins)
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from x402_bridge_enhanced import X402Bridge, X402Error, EscrowStatus


class ArbitrationSimulator:
    """
    Complete arbitration simulation environment.
    
    Simulates the entire dispute resolution lifecycle:
    1. Transaction initiation with escrow payment
    2. Dispute filing by buyer
    3. Evidence collection from both parties
    4. Automated arbitration decision
    5. X402 fund distribution based on verdict
    """
    
    def __init__(self, mock_mode: bool = True):
        """
        Initialize the arbitration simulator.
        
        Args:
            mock_mode: If True, use mock X402 bridge for testing
        """
        self.x402_bridge = X402Bridge(mock_mode=mock_mode)
        self.disputes = {}
        self.transactions = {}
        
    def create_transaction(
        self,
        buyer_id: str,
        seller_id: str,
        amount: float,
        asset: str = "USDC",
        contract_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new transaction with escrow payment.
        
        Args:
            buyer_id: Buyer's agent ID
            seller_id: Seller's agent ID
            amount: Transaction amount
            asset: Payment asset
            contract_hash: Hash of the contract deliverables
            
        Returns:
            Transaction details including escrow_id
        """
        print(f"\n{'='*60}")
        print(f"Creating transaction: {buyer_id} -> {seller_id}")
        print(f"Amount: {amount} {asset}")
        print(f"{'='*60}")
        
        # Check buyer's balance
        balance = self.x402_bridge.check_balance(buyer_id, asset)
        print(f"Buyer balance: {balance['balance']} {asset}")
        
        if balance['balance'] < amount:
            raise X402Error(
                code=1002,
                message=f"Insufficient balance: {balance['balance']} < {amount}"
            )
        
        # Initiate escrow payment
        escrow_result = self.x402_bridge.initiate_escrow_payment(
            sender_id=buyer_id,
            receiver_id=seller_id,
            amount=amount,
            asset=asset,
            contract_hash=contract_hash
        )
        
        tx_id = escrow_result['escrow_id']
        self.transactions[tx_id] = {
            'tx_id': tx_id,
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'amount': amount,
            'asset': asset,
            'contract_hash': contract_hash,
            'file_hash': None,
            'status': 'escrow_locked',
            'created_at': datetime.now().isoformat()
        }
        
        print(f"Transaction created: {tx_id}")
        print(f"Status: {escrow_result['status']}")
        
        return self.transactions[tx_id]
    
    def submit_delivery(
        self,
        tx_id: str,
        file_hash: str
    ) -> Dict[str, Any]:
        """
        Seller submits the delivered product.
        
        Args:
            tx_id: Transaction ID
            file_hash: Hash of the delivered file
            
        Returns:
            Updated transaction details
        """
        print(f"\n{'='*60}")
        print(f"Seller submitting delivery for {tx_id}")
        print(f"File hash: {file_hash}")
        print(f"{'='*60}")
        
        if tx_id not in self.transactions:
            raise ValueError(f"Transaction not found: {tx_id}")
        
        tx = self.transactions[tx_id]
        tx['file_hash'] = file_hash
        tx['status'] = 'delivered'
        tx['delivered_at'] = datetime.now().isoformat()
        
        print(f"Delivery submitted successfully")
        print(f"New status: {tx['status']}")
        
        return tx
    
    def initiate_dispute(
        self,
        tx_id: str,
        reason: str,
        evidence: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Buyer initiates a dispute.
        
        Args:
            tx_id: Transaction ID
            reason: Reason for dispute
            evidence: List of evidence items
            
        Returns:
            Dispute case details
        """
        print(f"\n{'='*60}")
        print(f"BUYER INITIATING DISPUTE")
        print(f"Transaction: {tx_id}")
        print(f"Reason: {reason}")
        print(f"{'='*60}")
        
        if tx_id not in self.transactions:
            raise ValueError(f"Transaction not found: {tx_id}")
        
        tx = self.transactions[tx_id]
        tx['status'] = 'disputed'
        tx['disputed_at'] = datetime.now().isoformat()
        
        dispute_id = f"DISPUTE_{tx_id}"
        self.disputes[dispute_id] = {
            'dispute_id': dispute_id,
            'tx_id': tx_id,
            'reason': reason,
            'evidence': evidence or [],
            'status': 'under_review',
            'created_at': datetime.now().isoformat()
        }
        
        print(f"Dispute created: {dispute_id}")
        print(f"Status: {self.disputes[dispute_id]['status']}")
        
        return self.disputes[dispute_id]
    
    def arbitrate(
        self,
        dispute_id: str
    ) -> Dict[str, Any]:
        """
        Execute automated arbitration.
        
        Compares contract_hash with file_hash to determine verdict:
        - Match: Seller wins (product delivered as promised)
        - Mismatch: Buyer wins (product not as described)
        - No file: Buyer wins (seller didn't deliver)
        
        Args:
            dispute_id: Dispute case ID
            
        Returns:
            Arbitration result with verdict
        """
        print(f"\n{'='*60}")
        print(f"ARBITRATION PROCESS")
        print(f"Dispute: {dispute_id}")
        print(f"{'='*60}")
        
        if dispute_id not in self.disputes:
            raise ValueError(f"Dispute not found: {dispute_id}")
        
        dispute = self.disputes[dispute_id]
        tx = self.transactions[dispute['tx_id']]
        
        contract_hash = tx.get('contract_hash')
        file_hash = tx.get('file_hash')
        
        print(f"Contract hash: {contract_hash}")
        print(f"File hash: {file_hash}")
        
        # Arbitration logic
        if not file_hash:
            verdict = "buyer_wins"
            reason = "Seller did not deliver the file"
        elif contract_hash == file_hash:
            verdict = "seller_wins"
            reason = "Contract hash matches delivered file"
        else:
            verdict = "buyer_wins"
            reason = "Delivered file hash does not match contract hash"
        
        arbitration_result = {
            'dispute_id': dispute_id,
            'tx_id': tx['tx_id'],
            'verdict': verdict,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        dispute['status'] = 'arbitrated'
        dispute['verdict'] = verdict
        dispute['arbitration_result'] = arbitration_result
        
        print(f"\nVerdict: {verdict}")
        print(f"Reason: {reason}")
        
        return arbitration_result
    
    def execute_verdict(
        self,
        dispute_id: str
    ) -> Dict[str, Any]:
        """
        Execute the arbitration verdict via X402.
        
        - If seller wins: Release funds to seller
        - If buyer wins: Refund to buyer
        
        Args:
            dispute_id: Dispute case ID
            
        Returns:
            Execution result with transaction hash
        """
        print(f"\n{'='*60}")
        print(f"EXECUTING VERDICT")
        print(f"Dispute: {dispute_id}")
        print(f"{'='*60}")
        
        if dispute_id not in self.disputes:
            raise ValueError(f"Dispute not found: {dispute_id}")
        
        dispute = self.disputes[dispute_id]
        if 'verdict' not in dispute:
            raise ValueError("Dispute not yet arbitrated")
        
        tx = self.transactions[dispute['tx_id']]
        verdict = dispute['verdict']
        escrow_id = tx['tx_id']
        
        # Determine recipient based on verdict
        if verdict == "seller_wins":
            recipient = tx['seller_id']
            print(f"Releasing {tx['amount']} {tx['asset']} to SELLER")
        else:
            recipient = tx['buyer_id']
            print(f"Refunding {tx['amount']} {tx['asset']} to BUYER")
        
        # Execute X402 fund release
        result = self.x402_bridge.release_funds(
            escrow_id=escrow_id,
            recipient=recipient,
            verdict=verdict
        )
        
        # Update transaction status
        tx['status'] = 'refunded' if verdict == 'buyer_wins' else 'completed'
        tx['settled_at'] = datetime.now().isoformat()
        tx['settlement_tx'] = result['tx_hash']
        
        dispute['status'] = 'executed'
        dispute['execution_result'] = result
        
        print(f"\nExecution complete:")
        print(f"Transaction hash: {result['tx_hash']}")
        print(f"New status: {tx['status']}")
        
        return result
    
    def run_full_scenario(
        self,
        scenario: str = "normal_completion"
    ) -> Dict[str, Any]:
        """
        Run a complete arbitration scenario.
        
        Args:
            scenario: One of:
                - "normal_completion": Seller delivers correct product
                - "quality_dispute": Product doesn't match contract
                - "non_delivery": Seller doesn't deliver
                
        Returns:
            Complete scenario execution log
        """
        print(f"\n{'#'*60}")
        print(f"# SCENARIO: {scenario.upper()}")
        print(f"{'#'*60}")
        
        if scenario == "normal_completion":
            return self._scenario_normal()
        elif scenario == "quality_dispute":
            return self._scenario_quality_dispute()
        elif scenario == "non_delivery":
            return self._scenario_non_delivery()
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
    
    def _scenario_normal(self) -> Dict[str, Any]:
        """Normal completion: Seller delivers correct product"""
        # Create transaction
        tx = self.create_transaction(
            buyer_id="buyer_001",
            seller_id="seller_002",
            amount=500.0,
            contract_hash="abc123"
        )
        
        # Seller delivers
        self.submit_delivery(
            tx_id=tx['tx_id'],
            file_hash="abc123"  # Matches contract
        )
        
        # No dispute needed - transaction completes normally
        result = self.x402_bridge.release_funds(
            escrow_id=tx['tx_id'],
            recipient=tx['seller_id'],
            verdict="seller_wins"
        )
        
        tx['status'] = 'completed'
        
        return {
            'scenario': 'normal_completion',
            'result': 'seller_wins',
            'tx': tx
        }
    
    def _scenario_quality_dispute(self) -> Dict[str, Any]:
        """Quality dispute: Product doesn't match contract"""
        # Create transaction
        tx = self.create_transaction(
            buyer_id="buyer_001",
            seller_id="seller_002",
            amount=500.0,
            contract_hash="abc123"
        )
        
        # Seller delivers wrong product
        self.submit_delivery(
            tx_id=tx['tx_id'],
            file_hash="xyz789"  # Doesn't match contract
        )
        
        # Buyer initiates dispute
        dispute = self.initiate_dispute(
            tx_id=tx['tx_id'],
            reason="Product quality does not match contract description",
            evidence=[
                {"type": "screenshot", "url": "evidence_1.png"},
                {"type": "log", "content": "Product failed validation"}
            ]
        )
        
        # Arbitration
        arbitration = self.arbitrate(dispute['dispute_id'])
        
        # Execute verdict
        execution = self.execute_verdict(dispute['dispute_id'])
        
        return {
            'scenario': 'quality_dispute',
            'result': 'buyer_wins',
            'tx': tx,
            'dispute': dispute,
            'arbitration': arbitration,
            'execution': execution
        }
    
    def _scenario_non_delivery(self) -> Dict[str, Any]:
        """Non-delivery: Seller doesn't deliver"""
        # Create transaction
        tx = self.create_transaction(
            buyer_id="buyer_001",
            seller_id="seller_002",
            amount=500.0,
            contract_hash="abc123"
        )
        
        # Seller doesn't deliver - buyer initiates dispute
        dispute = self.initiate_dispute(
            tx_id=tx['tx_id'],
            reason="Seller failed to deliver the product",
            evidence=[
                {"type": "timestamp", "content": "Delivery deadline passed"}
            ]
        )
        
        # Arbitration (will detect missing file_hash)
        arbitration = self.arbitrate(dispute['dispute_id'])
        
        # Execute verdict
        execution = self.execute_verdict(dispute['dispute_id'])
        
        return {
            'scenario': 'non_delivery',
            'result': 'buyer_wins',
            'tx': tx,
            'dispute': dispute,
            'arbitration': arbitration,
            'execution': execution
        }


def main():
    """Run all arbitration scenarios"""
    simulator = ArbitrationSimulator(mock_mode=True)
    
    results = []
    
    # Run all scenarios
    scenarios = [
        "normal_completion",
        "quality_dispute",
        "non_delivery"
    ]
    
    for scenario in scenarios:
        try:
            result = simulator.run_full_scenario(scenario)
            results.append(result)
            print(f"\n✓ Scenario '{scenario}' completed successfully")
        except Exception as e:
            print(f"\n✗ Scenario '{scenario}' failed: {str(e)}")
            results.append({
                'scenario': scenario,
                'error': str(e)
            })
    
    # Print summary
    print(f"\n{'#'*60}")
    print(f"# SIMULATION SUMMARY")
    print(f"{'#'*60}")
    
    for result in results:
        status = "✓ PASSED" if 'error' not in result else f"✗ FAILED: {result['error']}"
        print(f"\n{result['scenario']}: {status}")
        if 'result' in result:
            print(f"  Verdict: {result['result']}")
    
    print(f"\n{'='*60}")
    print("Simulation complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
