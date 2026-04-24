"""
Arbitration Engine and X402 Integration Tests
"""

import pytest
import asyncio
import hashlib
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.anchor.arbitration_timer import ArbitrationTimerService
from src.utils.async_task_processor import AsyncTaskProcessor


class TestArbitrationTimerService:
    def test_initialization(self):
        service = ArbitrationTimerService()
        assert service.countdowns == {}
        assert service.running == False
    
    @pytest.mark.asyncio
    async def test_start_arbitration_countdown(self):
        service = ArbitrationTimerService()
        task_processor_mock = AsyncMock(spec=AsyncTaskProcessor)
        
        # Initialize the service
        service.initialize(
            db_path=":memory:",
            task_processor=task_processor_mock,
            x402_bridge=None,
            github_anchor=None,
            x402_anchor=None
        )
        
        # Start a countdown
        await service.start_arbitration_countdown(tx_id="test_tx_001", hours=48)
        
        # Verify the countdown was added
        assert "test_tx_001" in service.countdowns
        assert service.countdowns["test_tx_001"]["hours"] == 48
        assert service.countdowns["test_tx_001"]["status"] == "counting"
    
    def test_get_countdown_status(self):
        service = ArbitrationTimerService()
        service.countdowns["test_tx_002"] = {
            "tx_id": "test_tx_002",
            "deadline": "2025-05-01T00:00:00",
            "hours": 48,
            "status": "counting"
        }
        
        status = service.get_countdown_status("test_tx_002")
        assert status is not None
        assert status["tx_id"] == "test_tx_002"
        assert status["status"] == "counting"
    
    @pytest.mark.asyncio
    async def test_cancel_countdown(self):
        service = ArbitrationTimerService()
        service.countdowns["test_tx_003"] = {
            "tx_id": "test_tx_003",
            "status": "counting"
        }
        
        await service.cancel_countdown("test_tx_003")
        
        assert "test_tx_003" not in service.countdowns


class TestAsyncTaskProcessorArbitration:
    @pytest.mark.asyncio
    async def test_async_task_submission(self):
        processor = AsyncTaskProcessor(max_workers=2)
        await processor.start()
        
        processed = []
        
        async def test_task(value):
            await asyncio.sleep(0.1)
            processed.append(value)
            return value
        
        # Submit multiple tasks
        await processor.submit_task(test_task, 1)
        await processor.submit_task(test_task, 2)
        await processor.submit_task(test_task, 3)
        
        # Give time to process
        await asyncio.sleep(0.5)
        
        assert len(processed) == 3
        assert processed == [1, 2, 3]
        
        await processor.stop()


class TestX402Bridge:
    def test_initialization_without_api_key(self):
        from src.x402.bridge import X402Bridge
        bridge = X402Bridge(api_key=None)
        assert bridge.enabled == False
    
    @pytest.mark.asyncio
    async def test_x402_release_funds_simulation(self):
        from src.x402.bridge import X402Bridge
        bridge = X402Bridge(api_key=None)
        result = await bridge.release_funds("escrow_001", "address_001", "seller_wins")
        
        assert "status" in result
        assert result["status"] in ["settled", "simulated"]


class TestDualAnchorArbitration:
    @pytest.mark.asyncio
    async def test_anchor_arbitration_result(self):
        from src.anchor.dual_anchor import DualAnchorService
        
        mock_github = AsyncMock()
        mock_x402 = AsyncMock()
        mock_x402.anchor_commit_hash = AsyncMock(return_value={
            "success": True,
            "tx_hash": "0x1234567890abcdef1234567890abcdef12345678"
        })
        
        dual = DualAnchorService(mock_github, mock_x402)
        
        result = await dual.anchor_arbitration_result(
            arbitration_id="arb_001",
            verdict="seller_wins",
            commit_hash="commit_hash_001",
            metadata={"case_id": "test_001"}
        )
        
        assert result["arbitration_id"] == "arb_001"
        assert result["verdict"] == "seller_wins"
        assert result["x402_success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
