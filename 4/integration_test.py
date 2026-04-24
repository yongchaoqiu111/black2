"""
Black2 SDK - Full Integration Test

This test simulates the complete B2P + X402 transaction lifecycle:
1. Buyer checks seller's reputation
2. Buyer initiates escrow payment (Mock Mode)
3. Seller confirms and submits deliverable
4. Buyer initiates dispute (simulating quality issue)
5. Automated arbitration executes
6. X402 releases funds based on verdict

This demonstrates the core value proposition of Black2 Protocol:
- Trust layer for AI-to-AI transactions
- Secure escrow payments via X402
- Automated dispute resolution
- Privacy protection

Usage:
    python integration_test.py
    
Requirements:
    - Python 3.8+
    - black2-sdk (or run in mock mode)
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from local files (for testing before integration)
from x402_bridge_enhanced import X402Bridge, X402Error, X402ErrorCode, EscrowStatus
from test_arbitrator import ArbitrationSimulator


class IntegrationTest:
    """
    Integration test for Black2 SDK.
    
    Simulates a complete transaction flow from reputation check to final settlement.
    """
    
    def __init__(self, mock_mode: bool = True):
        """
        Initialize integration test.
        
        Args:
            mock_mode: If True, use mock mode for all operations
        """
        self.mock_mode = mock_mode
        self.x402_bridge = X402Bridge(mock_mode=mock_mode)
        self.arbitration_sim = ArbitrationSimulator(mock_mode=mock_mode)
        
        # Test state
        self.test_results: Dict[str, Any] = {
            'start_time': datetime.now().isoformat(),
            'steps': [],
            'errors': [],
            'success': False
        }
    
    def log_step(self, step_name: str, status: str, details: Optional[Dict] = None):
        """
        Log a test step.
        
        Args:
            step_name: Name of the step
            status: Status ('PASS', 'FAIL', 'INFO')
            details: Additional details
        """
        step = {
            'step': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results['steps'].append(step)
        
        # Print to console
        emoji = "✓" if status == "PASS" else "✗" if status == "FAIL" else "ℹ"
        print(f"{emoji} {step_name}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
    
    def step_1_reputation_check(self) -> bool:
        """
        Step 1: Buyer checks seller's reputation.
        
        In a real scenario, this would query the reputation engine.
        For this test, we simulate a good reputation score.
        """
        print("\n" + "="*60)
        print("Step 1: Reputation Check")
        print("="*60)
        
        try:
            # Simulate reputation data
            seller_id = "seller_002"
            reputation_data = {
                'agent_id': seller_id,
                'total_score': 850,
                'risk_level': 'LOW',
                'friction_coefficient': 0.15,
                'successful_transactions': 127,
                'dispute_count': 2,
                'win_rate': 0.98
            }
            
            self.log_step(
                "Query seller reputation",
                "PASS",
                {
                    'seller_id': seller_id,
                    'risk_level': reputation_data['risk_level'],
                    'score': reputation_data['total_score']
                }
            )
            
            # Check if reputation is acceptable
            if reputation_data['risk_level'] in ['LOW', 'MEDIUM']:
                self.log_step(
                    "Reputation assessment",
                    "PASS",
                    {'decision': 'Proceed with transaction'}
                )
                return True
            else:
                self.log_step(
                    "Reputation assessment",
                    "FAIL",
                    {'decision': 'Too risky, abort transaction'}
                )
                return False
                
        except Exception as e:
            self.log_step(
                "Reputation check",
                "FAIL",
                {'error': str(e)}
            )
            self.test_results['errors'].append(str(e))
            return False
    
    def step_2_escrow_payment(self) -> Optional[str]:
        """
        Step 2: Buyer initiates escrow payment.
        
        Returns:
            escrow_id if successful, None otherwise
        """
        print("\n" + "="*60)
        print("Step 2: Escrow Payment Initiation")
        print("="*60)
        
        try:
            buyer_id = "buyer_001"
            seller_id = "seller_002"
            amount = 500.0
            asset = "USDC"
            contract_hash = "abc123def456"
            
            # Check buyer's balance
            balance = self.x402_bridge.check_balance(buyer_id, asset)
            self.log_step(
                "Check buyer balance",
                "PASS",
                {
                    'balance': balance['balance'],
                    'asset': balance['asset']
                }
            )
            
            # Initiate escrow
            escrow_result = self.x402_bridge.initiate_escrow_payment(
                sender_id=buyer_id,
                receiver_id=seller_id,
                amount=amount,
                asset=asset,
                contract_hash=contract_hash
            )
            
            self.log_step(
                "Initiate escrow payment",
                "PASS",
                {
                    'escrow_id': escrow_result['escrow_id'],
                    'status': escrow_result['status'],
                    'amount': f"{amount} {asset}"
                }
            )
            
            return escrow_result['escrow_id']
            
        except X402Error as e:
            self.log_step(
                "Escrow payment",
                "FAIL",
                {
                    'error_code': e.code.name,
                    'error_message': e.message
                }
            )
            self.test_results['errors'].append(str(e))
            return None
        except Exception as e:
            self.log_step(
                "Escrow payment",
                "FAIL",
                {'error': str(e)}
            )
            self.test_results['errors'].append(str(e))
            return None
    
    def step_3_seller_delivery(self, escrow_id: str) -> bool:
        """
        Step 3: Seller confirms and submits deliverable.
        
        Args:
            escrow_id: The escrow ID
            
        Returns:
            True if successful
        """
        print("\n" + "="*60)
        print("Step 3: Seller Delivery")
        print("="*60)
        
        try:
            # Simulate seller submitting deliverable
            # In this scenario, seller submits WRONG hash (causing dispute)
            file_hash = "xyz789"  # Does NOT match contract_hash "abc123def456"
            
            self.log_step(
                "Seller submits deliverable",
                "INFO",
                {
                    'file_hash': file_hash,
                    'note': 'Hash does NOT match contract (simulating quality issue)'
                }
            )
            
            # Store for later use in dispute
            self.test_results['delivered_hash'] = file_hash
            
            return True
            
        except Exception as e:
            self.log_step(
                "Seller delivery",
                "FAIL",
                {'error': str(e)}
            )
            self.test_results['errors'].append(str(e))
            return False
    
    def step_4_buyer_dispute(self, escrow_id: str) -> bool:
        """
        Step 4: Buyer initiates dispute.
        
        Args:
            escrow_id: The escrow ID
            
        Returns:
            True if successful
        """
        print("\n" + "="*60)
        print("Step 4: Buyer Dispute")
        print("="*60)
        
        try:
            reason = "Product quality does not match contract description"
            evidence = [
                {"type": "comparison", "detail": "Hash mismatch: expected abc123def456, got xyz789"},
                {"type": "screenshot", "url": "evidence_1.png"},
            ]
            
            self.log_step(
                "Buyer initiates dispute",
                "PASS",
                {
                    'reason': reason,
                    'evidence_count': len(evidence)
                }
            )
            
            # Store dispute info
            self.test_results['dispute'] = {
                'escrow_id': escrow_id,
                'reason': reason,
                'evidence': evidence
            }
            
            return True
            
        except Exception as e:
            self.log_step(
                "Buyer dispute",
                "FAIL",
                {'error': str(e)}
            )
            self.test_results['errors'].append(str(e))
            return False
    
    def step_5_arbitration(self) -> Optional[Dict[str, Any]]:
        """
        Step 5: Automated arbitration.
        
        Returns:
            Arbitration result if successful
        """
        print("\n" + "="*60)
        print("Step 5: Automated Arbitration")
        print("="*60)
        
        try:
            # Get dispute info
            dispute = self.test_results.get('dispute')
            if not dispute:
                raise ValueError("No dispute found")
            
            escrow_id = dispute['escrow_id']
            
            # Simulate arbitration logic
            contract_hash = "abc123def456"
            delivered_hash = self.test_results.get('delivered_hash', '')
            
            self.log_step(
                "Arbitration comparison",
                "INFO",
                {
                    'contract_hash': contract_hash,
                    'delivered_hash': delivered_hash,
                    'match': contract_hash == delivered_hash
                }
            )
            
            # Determine verdict
            if not delivered_hash:
                verdict = "buyer_wins"
                reason = "Seller did not deliver"
            elif contract_hash == delivered_hash:
                verdict = "seller_wins"
                reason = "Contract hash matches delivered file"
            else:
                verdict = "buyer_wins"
                reason = "Delivered file hash does not match contract hash"
            
            arbitration_result = {
                'verdict': verdict,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log_step(
                "Arbitration verdict",
                "PASS",
                {
                    'verdict': verdict,
                    'reason': reason
                }
            )
            
            self.test_results['arbitration'] = arbitration_result
            return arbitration_result
            
        except Exception as e:
            self.log_step(
                "Arbitration",
                "FAIL",
                {'error': str(e)}
            )
            self.test_results['errors'].append(str(e))
            return None
    
    def step_6_fund_settlement(self, escrow_id: str, arbitration_result: Dict[str, Any]) -> bool:
        """
        Step 6: X402 fund settlement based on verdict.
        
        Args:
            escrow_id: The escrow ID
            arbitration_result: Result from arbitration
            
        Returns:
            True if successful
        """
        print("\n" + "="*60)
        print("Step 6: Fund Settlement")
        print("="*60)
        
        try:
            verdict = arbitration_result['verdict']
            
            # Determine recipient
            if verdict == "seller_wins":
                recipient = "seller_002"
                action = "Release funds to seller"
            else:
                recipient = "buyer_001"
                action = "Refund to buyer"
            
            self.log_step(
                "Determine recipient",
                "INFO",
                {
                    'verdict': verdict,
                    'recipient': recipient,
                    'action': action
                }
            )
            
            # Execute X402 settlement
            settlement_result = self.x402_bridge.release_funds(
                escrow_id=escrow_id,
                recipient=recipient,
                verdict=verdict
            )
            
            self.log_step(
                "X402 fund release",
                "PASS",
                {
                    'status': settlement_result['status'],
                    'tx_hash': settlement_result['tx_hash'],
                    'recipient': recipient
                }
            )
            
            self.test_results['settlement'] = settlement_result
            return True
            
        except X402Error as e:
            self.log_step(
                "Fund settlement",
                "FAIL",
                {
                    'error_code': e.code.name,
                    'error_message': e.message
                }
            )
            self.test_results['errors'].append(str(e))
            return False
        except Exception as e:
            self.log_step(
                "Fund settlement",
                "FAIL",
                {'error': str(e)}
            )
            self.test_results['errors'].append(str(e))
            return False
    
    def run_full_test(self) -> bool:
        """
        Run the complete integration test.
        
        Returns:
            True if all steps passed
        """
        print("\n" + "#"*60)
        print("# Black2 SDK - Full Integration Test")
        print("#"*60)
        print(f"\nStarted at: {self.test_results['start_time']}")
        print(f"Mode: {'Mock' if self.mock_mode else 'Production'}")
        
        # Step 1: Reputation Check
        if not self.step_1_reputation_check():
            print("\n✗ Transaction aborted due to poor reputation")
            self.test_results['success'] = False
            return False
        
        # Step 2: Escrow Payment
        escrow_id = self.step_2_escrow_payment()
        if not escrow_id:
            print("\n✗ Failed to initiate escrow payment")
            self.test_results['success'] = False
            return False
        
        # Step 3: Seller Delivery
        if not self.step_3_seller_delivery(escrow_id):
            print("\n✗ Seller delivery failed")
            self.test_results['success'] = False
            return False
        
        # Step 4: Buyer Dispute
        if not self.step_4_buyer_dispute(escrow_id):
            print("\n✗ Buyer dispute failed")
            self.test_results['success'] = False
            return False
        
        # Step 5: Arbitration
        arbitration_result = self.step_5_arbitration()
        if not arbitration_result:
            print("\n✗ Arbitration failed")
            self.test_results['success'] = False
            return False
        
        # Step 6: Fund Settlement
        if not self.step_6_fund_settlement(escrow_id, arbitration_result):
            print("\n✗ Fund settlement failed")
            self.test_results['success'] = False
            return False
        
        # All steps completed
        self.test_results['end_time'] = datetime.now().isoformat()
        self.test_results['success'] = True
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("INTEGRATION TEST SUMMARY")
        print("="*60)
        
        total_steps = len(self.test_results['steps'])
        passed_steps = sum(1 for step in self.test_results['steps'] if step['status'] == 'PASS')
        
        print(f"\nTotal Steps: {total_steps}")
        print(f"Passed: {passed_steps}")
        print(f"Failed: {total_steps - passed_steps}")
        
        if self.test_results['errors']:
            print(f"\nErrors ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results['errors'], 1):
                print(f"  {i}. {error}")
        
        print(f"\nOverall Result: {'✓ PASSED' if self.test_results['success'] else '✗ FAILED'}")
        print(f"Duration: {self.test_results['end_time']} - {self.test_results['start_time']}")
        
        # Print key outcomes
        if 'arbitration' in self.test_results:
            arb = self.test_results['arbitration']
            print(f"\nArbitration Verdict: {arb['verdict']}")
            print(f"Reason: {arb['reason']}")
        
        if 'settlement' in self.test_results:
            settlement = self.test_results['settlement']
            print(f"\nSettlement Status: {settlement['status']}")
            print(f"Transaction Hash: {settlement['tx_hash']}")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("Black2 SDK - Integration Test Suite")
    print("="*60)
    print("\nThis test simulates a complete B2P + X402 transaction:")
    print("1. Reputation Check → 2. Escrow Payment → 3. Delivery")
    print("4. Dispute → 5. Arbitration → 6. Settlement")
    print("\n" + "="*60)
    
    # Create and run test
    test = IntegrationTest(mock_mode=True)
    success = test.run_full_test()
    
    # Return exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
