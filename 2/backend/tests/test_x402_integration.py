"""
X402 Integration Tests
"""

import pytest
import asyncio
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from anchor.x402_anchor import X402OnChainAnchor
from anchor.dual_anchor import DualAnchorService
from utils.async_task_processor import AsyncTaskProcessor


class TestX402OnChainAnchor:
    def test_supported_chains(self):
        anchor = X402OnChainAnchor()
        assert "base" in anchor.SUPPORTED_CHAINS
        assert anchor.SUPPORTED_CHAINS["base"] == 8453

    def test_calculate_merkle_root(self):
        anchor = X402OnChainAnchor()
        
        assert anchor._calculate_merkle_root([]) == hashlib.sha256(b"empty").hexdigest()
        
        single_hash = "abc123"
        assert anchor._calculate_merkle_root([single_hash]) == single_hash
        
        hashes = ["a", "b", "c", "d"]
        result = anchor._calculate_merkle_root(hashes)
        assert len(result) == 64

    @pytest.mark.asyncio
    async def test_anchor_commit_hash_disabled(self):
        anchor = X402OnChainAnchor()
        anchor.enabled = False
        
        result = await anchor.anchor_commit_hash("test_hash", "test_type")
        assert not result["success"]
        assert "not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_verify_on_chain(self):
        anchor = X402OnChainAnchor()
        
        valid_hash = "0x" + "a" * 40
        assert await anchor.verify_on_chain("test", valid_hash)
        
        invalid_hash = "invalid"
        assert not await anchor.verify_on_chain("test", invalid_hash)


class TestDualAnchorService:
    @pytest.mark.asyncio
    async def test_anchor_arbitration_result(self):
        mock_github = AsyncMock()
        mock_x402 = AsyncMock()
        
        mock_x402.anchor_commit_hash = AsyncMock(return_value={
            "success": True,
            "tx_hash": "0x123"
        })
        
        dual = DualAnchorService(mock_github, mock_x402)
        
        result = await dual.anchor_arbitration_result(
            arbitration_id="arb123",
            verdict="seller_wins",
            commit_hash="commit123"
        )
        
        assert result["arbitration_id"] == "arb123"
        assert result["x402_tx_hash"] == "0x123"
        assert result["x402_success"] is True

    @pytest.mark.asyncio
    async def test_pending_chain_anchors(self):
        mock_github = AsyncMock()
        mock_x402 = AsyncMock()
        
        mock_x402.anchor_commit_hash = AsyncMock(side_effect=[
            {"success": False, "error": "temp_error"},
            {"success": True, "tx_hash": "0x123"}
        ])
        
        dual = DualAnchorService(mock_github, mock_x402)
        
        await dual.anchor_arbitration_result(
            arbitration_id="arb123",
            verdict="seller_wins",
            commit_hash="commit123"
        )
        
        assert await dual.get_pending_count() == 1
        
        await dual.retry_pending_chain_anchors()
        
        assert await dual.get_pending_count() == 0


class TestAsyncTaskProcessor:
    @pytest.mark.asyncio
    async def test_task_submit_and_process(self):
        processor = AsyncTaskProcessor(max_workers=1)
        await processor.start()
        
        result_event = asyncio.Event()
        processed_value = None
        
        async def sample_task(value):
            nonlocal processed_value
            processed_value = value
            result_event.set()
            return value
        
        await processor.submit_task(sample_task, 42)
        
        await asyncio.wait_for(result_event.wait(), 5)
        
        assert processed_value == 42
        assert processor.get_stats()["processed_count"] == 1
        
        await processor.stop()

    @pytest.mark.asyncio
    async def test_batch_processing(self):
        processor = AsyncTaskProcessor(max_workers=2)
        await processor.start()
        
        results = []
        
        async def task_func(x):
            await asyncio.sleep(0.1)
            results.append(x)
        
        for i in range(5):
            await processor.submit_task(task_func, i)
        
        await asyncio.sleep(1)
        
        assert len(results) == 5
        await processor.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])