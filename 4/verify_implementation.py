"""
Quick Verification Script for Black2 SDK

This script runs a quick verification of all implemented features:
1. X402 Bridge initialization (Mock Mode)
2. Error handling
3. Escrow payment flow
4. Arbitration simulation
5. All three test scenarios

Usage:
    python verify_implementation.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from x402_bridge_enhanced import X402Bridge, X402Error, X402ErrorCode, EscrowStatus
from test_arbitrator import ArbitrationSimulator


def test_x402_bridge_initialization():
    """Test 1: X402 Bridge initialization"""
    print("\n" + "="*60)
    print("Test 1: X402 Bridge Initialization")
    print("="*60)
    
    try:
        # Test mock mode initialization
        bridge = X402Bridge(mock_mode=True)
        print("✓ Mock mode initialization: PASSED")
        
        # Test attributes
        assert hasattr(bridge, 'api_key')
        assert hasattr(bridge, 'mock_mode')
        assert hasattr(bridge, 'SUPPORTED_ASSETS')
        print("✓ Required attributes exist: PASSED")
        
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {str(e)}")
        return False


def test_error_handling():
    """Test 2: Error handling"""
    print("\n" + "="*60)
    print("Test 2: Error Handling")
    print("="*60)
    
    bridge = X402Bridge(mock_mode=True)
    
    try:
        # Test invalid asset
        try:
            bridge.check_balance("agent_001", "INVALID_TOKEN")
            print("✗ Should have raised error for invalid asset")
            return False
        except X402Error as e:
            assert e.code == X402ErrorCode.INVALID_ADDRESS
            print("✓ Invalid asset error handling: PASSED")
        
        # Test invalid amount
        try:
            bridge.initiate_escrow_payment("buyer", "seller", -100.0)
            print("✗ Should have raised error for negative amount")
            return False
        except X402Error as e:
            assert e.code == X402ErrorCode.INSUFFICIENT_BALANCE
            print("✓ Invalid amount error handling: PASSED")
        
        return True
    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")
        return False


def test_escrow_payment_flow():
    """Test 3: Escrow payment flow"""
    print("\n" + "="*60)
    print("Test 3: Escrow Payment Flow")
    print("="*60)
    
    bridge = X402Bridge(mock_mode=True)
    
    try:
        # Initiate escrow
        result = bridge.initiate_escrow_payment(
            sender_id="buyer_001",
            receiver_id="seller_002",
            amount=500.0,
            asset="USDC"
        )
        
        assert result['status'] == 'locked'
        assert 'escrow_id' in result
        assert result['amount'] == 500.0
        print("✓ Escrow initiation: PASSED")
        
        # Check balance
        balance = bridge.check_balance("buyer_001", "USDC")
        assert 'balance' in balance
        assert balance['balance'] > 0
        print("✓ Balance check: PASSED")
        
        # Release funds
        release_result = bridge.release_funds(
            escrow_id=result['escrow_id'],
            recipient="seller_002",
            verdict="seller_wins"
        )
        
        assert release_result['status'] == 'settled'
        assert 'tx_hash' in release_result
        print("✓ Fund release: PASSED")
        
        return True
    except Exception as e:
        print(f"✗ Escrow flow test failed: {str(e)}")
        return False


def test_arbitration_scenarios():
    """Test 4: All arbitration scenarios"""
    print("\n" + "="*60)
    print("Test 4: Arbitration Scenarios")
    print("="*60)
    
    simulator = ArbitrationSimulator(mock_mode=True)
    
    scenarios = [
        ("normal_completion", "seller_wins"),
        ("quality_dispute", "buyer_wins"),
        ("non_delivery", "buyer_wins")
    ]
    
    all_passed = True
    
    for scenario_name, expected_verdict in scenarios:
        try:
            result = simulator.run_full_scenario(scenario_name)
            
            if 'error' in result:
                print(f"✗ {scenario_name}: FAILED - {result['error']}")
                all_passed = False
            elif result.get('result') == expected_verdict:
                print(f"✓ {scenario_name} ({expected_verdict}): PASSED")
            else:
                print(f"✗ {scenario_name}: Unexpected result")
                all_passed = False
                
        except Exception as e:
            print(f"✗ {scenario_name}: Exception - {str(e)}")
            all_passed = False
    
    return all_passed


def test_mock_vs_production_mode():
    """Test 5: Mock vs Production mode"""
    print("\n" + "="*60)
    print("Test 5: Mock vs Production Mode")
    print("="*60)
    
    try:
        # Test mock mode
        mock_bridge = X402Bridge(mock_mode=True)
        assert mock_bridge.mock_mode == True
        print("✓ Mock mode flag: PASSED")
        
        # Test production mode (without API key)
        prod_bridge = X402Bridge(mock_mode=False, api_key=None)
        # Should fallback to mock mode when no API key
        assert prod_bridge.mock_mode == True
        print("✓ Production mode fallback: PASSED")
        
        return True
    except Exception as e:
        print(f"✗ Mode test failed: {str(e)}")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "#"*60)
    print("# Black2 SDK - Implementation Verification")
    print("#"*60)
    print("\nRunning comprehensive tests...\n")
    
    tests = [
        ("X402 Bridge Initialization", test_x402_bridge_initialization),
        ("Error Handling", test_error_handling),
        ("Escrow Payment Flow", test_escrow_payment_flow),
        ("Arbitration Scenarios", test_arbitration_scenarios),
        ("Mock vs Production Mode", test_mock_vs_production_mode),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Implementation is complete.")
        print("\nNext steps:")
        print("1. Review INTEGRATION_GUIDE.md for integration instructions")
        print("2. Check COMPLETION_REPORT.md for detailed documentation")
        print("3. Run full test suite: python test_arbitrator.py")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
