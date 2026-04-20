"""
Anchor Service Tests
"""

import hashlib
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from anchor.anchor_service import AnchorService
from db.transaction_db import TransactionDB


class TestAnchorService:
    def test_calculate_root_hash_empty(self):
        mock_db = MagicMock()
        service = AnchorService(mock_db)

        result = service.calculate_root_hash([])
        assert result == hashlib.sha256(b"empty").hexdigest()

    def test_calculate_root_hash_single_transaction(self):
        mock_db = MagicMock()
        service = AnchorService(mock_db)

        transactions = [
            {
                "tx_hash": "abc123",
                "sender": "sender1",
                "receiver": "receiver1",
                "amount": 100.0,
                "fee": 1.0,
                "timestamp": "2026-04-20T10:00:00Z"
            }
        ]

        result = service.calculate_root_hash(transactions)
        assert len(result) == 64

    def test_calculate_root_hash_sorted_by_timestamp(self):
        mock_db = MagicMock()
        service = AnchorService(mock_db)

        transactions = [
            {
                "tx_hash": "abc123",
                "sender": "sender1",
                "receiver": "receiver1",
                "amount": 100.0,
                "fee": 1.0,
                "timestamp": "2026-04-20T12:00:00Z"
            },
            {
                "tx_hash": "def456",
                "sender": "sender2",
                "receiver": "receiver2",
                "amount": 200.0,
                "fee": 2.0,
                "timestamp": "2026-04-20T10:00:00Z"
            }
        ]

        result = service.calculate_root_hash(transactions)
        combined = "def456" + "abc123"
        expected = hashlib.sha256(combined.encode()).hexdigest()
        assert result == expected

    @pytest.mark.asyncio
    async def test_anchor_to_gist_success(self):
        mock_db = MagicMock()
        service = AnchorService(mock_db)
        service.github_token = "test_token"

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "html_url": "https://gist.github.com/test",
                "updated_at": "2026-04-20T10:00:00Z"
            }
            mock_response.raise_for_status = MagicMock()

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aexit__.return_value = AsyncMock()

            result = await service.anchor_to_gist(
                root_hash="test_hash",
                transaction_count=10,
                previous_anchor="prev_hash"
            )

            assert result["gist_url"] == "https://gist.github.com/test"
            assert result["gist_commit_hash"] == "2026-04-20T10:00:00Z"

    @pytest.mark.asyncio
    async def test_perform_anchor_no_transactions(self):
        mock_db = AsyncMock()
        mock_db.get_unanchored_transactions.return_value = []
        mock_db.get_latest_anchor.return_value = None

        service = AnchorService(mock_db)

        result = await service.perform_anchor()

        assert result is None


class TestTransactionDB:
    @pytest.mark.asyncio
    async def test_initialize_creates_tables(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        db = TransactionDB(db_path)

        await db.initialize()

        cursor = await db._db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = await cursor.fetchall()
        table_names = [t[0] for t in tables]

        assert "transactions" in table_names
        assert "anchor_records" in table_names

    @pytest.mark.asyncio
    async def test_add_transaction(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        db = TransactionDB(db_path)
        await db.initialize()

        tx_id = await db.add_transaction(
            tx_hash="tx123",
            sender="sender1",
            receiver="receiver1",
            amount=100.0,
            fee=1.0,
            timestamp="2026-04-20T10:00:00Z"
        )

        assert tx_id > 0

    @pytest.mark.asyncio
    async def test_get_unanchored_transactions(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        db = TransactionDB(db_path)
        await db.initialize()

        await db.add_transaction(
            tx_hash="tx123",
            sender="sender1",
            receiver="receiver1",
            amount=100.0,
            fee=1.0,
            timestamp="2026-04-20T10:00:00Z"
        )

        unanchored = await db.get_unanchored_transactions()
        assert len(unanchored) == 1
        assert unanchored[0]["tx_hash"] == "tx123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])