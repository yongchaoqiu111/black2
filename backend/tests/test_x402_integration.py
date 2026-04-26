"""
Tests for X402 fund release and arbitration fund pool integration.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.api.routes import complete_transaction, get_arbitration_fund_pool
from src.utils.api_response import APIResponse


@pytest.mark.asyncio
async def test_complete_transaction_with_x402_release():
    """Test that complete_transaction triggers X402 fund release"""
    
    tx_id = "test_tx_001"
    
    # Mock database transaction details
    mock_tx_details = {
        'amount': 100.0,
        'to_address': '0xseller123',
        'escrow_id': 'escrow_test_001'
    }
    
    # Mock X402 bridge response
    mock_release_result = MagicMock()
    mock_release_result.success = True
    mock_release_result.amount = 95.0  # 100 - 5% fee
    mock_release_result.tx_hash = '0xabc123...'
    mock_release_result.message = 'Funds released: 95.0 to 0xseller123 (fee: 5.0, arb: 0.0)'
    
    with patch('src.api.routes.get_transaction') as mock_get_tx, \
         patch('src.api.routes.update_transaction_status') as mock_update_status, \
         patch('src.api.routes.x402_bridge') as mock_x402, \
         patch('src.api.routes.record_fund_release') as mock_record_release:
        
        # Setup mocks
        async def async_get_tx(tx_id):
            return mock_tx_details
        
        mock_get_tx.side_effect = async_get_tx
        mock_x402.calculate_platform_fee.return_value = 5.0
        mock_x402.release_funds = AsyncMock(return_value=mock_release_result)
        mock_record_release.return_value = True
        
        # Call the endpoint
        result = await complete_transaction(tx_id)
        
        # Verify X402 was called
        mock_x402.calculate_platform_fee.assert_called_once_with(100.0)
        mock_x402.release_funds.assert_called_once_with(
            escrow_id='escrow_test_001',
            recipient='0xseller123',
            amount=100.0,
            verdict='completed',
            platform_fee=5.0,
            arbitration_fee=0.0
        )
        
        # Verify fund release was recorded
        mock_record_release.assert_called_once()
        
        # Verify response format
        assert result['code'] == 200
        assert result['data']['tx_id'] == tx_id


@pytest.mark.asyncio
async def test_complete_transaction_x402_failure_tolerance():
    """Test that transaction completion doesn't fail if X402 fails"""
    
    tx_id = "test_tx_002"
    
    mock_tx_details = {
        'amount': 100.0,
        'to_address': '0xseller456',
        'escrow_id': 'escrow_test_002'
    }
    
    with patch('src.api.routes.get_transaction') as mock_get_tx, \
         patch('src.api.routes.update_transaction_status') as mock_update_status, \
         patch('src.api.routes.x402_bridge') as mock_x402:
        
        async def async_get_tx(tx_id):
            return mock_tx_details
        
        mock_get_tx.side_effect = async_get_tx
        
        # Simulate X402 failure
        mock_x402.calculate_platform_fee.side_effect = Exception("X402 connection failed")
        
        # Call the endpoint - should not raise exception
        result = await complete_transaction(tx_id)
        
        # Should still succeed (X402 failure is logged but doesn't block)
        assert result['code'] == 200


@pytest.mark.asyncio
async def test_get_arbitration_fund_pool_success():
    """Test successful retrieval of arbitration fund pool"""
    
    mock_pool_data = {
        'total_balance': 1500.0,
        'total_injections': 15,
        'recent_injections': [
            {'amount': 100.0, 'source_tx_id': 'tx_001', 'reason': 'Penalty'},
            {'amount': 50.0, 'source_tx_id': 'tx_002', 'reason': 'Fine'}
        ]
    }
    
    with patch('src.api.routes.get_arbitration_fund_balance') as mock_get_pool:
        async def async_get_pool():
            return mock_pool_data
        
        mock_get_pool.side_effect = async_get_pool
        
        result = await get_arbitration_fund_pool()
        
        # Verify response structure
        assert result['code'] == 200
        assert result['message'] == 'Arbitration fund pool retrieved successfully'
        assert result['data']['total_balance'] == 1500.0
        assert result['data']['total_injections'] == 15
        assert len(result['data']['recent_injections']) == 2


@pytest.mark.asyncio
async def test_get_arbitration_fund_pool_error_handling():
    """Test error handling when fund pool query fails"""
    
    with patch('src.api.routes.get_arbitration_fund_balance') as mock_get_pool:
        # Simulate database error
        mock_get_pool.side_effect = Exception("Database connection failed")
        
        result = await get_arbitration_fund_pool()
        
        # Verify error response
        assert result['code'] == 5002
        assert 'Failed to retrieve fund pool' in result['message']
        assert result['data'] is None


@pytest.mark.asyncio
async def test_platform_fee_calculation_accuracy():
    """Test that platform fee is calculated correctly (5%)"""
    
    from src.x402.bridge import x402_bridge
    
    # Test various amounts
    test_cases = [
        (100.0, 5.0),
        (200.0, 10.0),
        (50.0, 2.5),
        (1000.0, 50.0)
    ]
    
    for amount, expected_fee in test_cases:
        fee = await x402_bridge.calculate_platform_fee(amount)
        assert abs(fee - expected_fee) < 0.01, f"Fee mismatch for {amount}: expected {expected_fee}, got {fee}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
