"""
Transaction Database Module

Provides database operations for transaction records.
"""

import aiosqlite
import os
from typing import Optional


class TransactionDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT UNIQUE NOT NULL,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                amount REAL NOT NULL,
                fee REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                anchor_hash TEXT,
                anchor_timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS anchor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_hash TEXT UNIQUE NOT NULL,
                transaction_count INTEGER NOT NULL,
                gist_url TEXT,
                gist_commit_hash TEXT,
                anchor_timestamp TEXT NOT NULL,
                previous_anchor TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._db.commit()

    async def close(self):
        if self._db:
            await self._db.close()

    async def add_transaction(self, tx_hash: str, sender: str, receiver: str, amount: float, fee: float, timestamp: str) -> int:
        cursor = await self._db.execute(
            """INSERT OR IGNORE INTO transactions (tx_hash, sender, receiver, amount, fee, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (tx_hash, sender, receiver, amount, fee, timestamp)
        )
        await self._db.commit()
        return cursor.lastrowid

    async def get_unanchored_transactions(self):
        cursor = await self._db.execute(
            """SELECT tx_hash, sender, receiver, amount, fee, timestamp
               FROM transactions
               WHERE anchor_hash IS NULL
               ORDER BY timestamp ASC"""
        )
        rows = await cursor.fetchall()
        return [
            {
                "tx_hash": row[0],
                "sender": row[1],
                "receiver": row[2],
                "amount": row[3],
                "fee": row[4],
                "timestamp": row[5]
            }
            for row in rows
        ]

    async def anchor_transactions(self, tx_hashes: list, anchor_hash: str, anchor_timestamp: str):
        for tx_hash in tx_hashes:
            await self._db.execute(
                """UPDATE transactions
                   SET anchor_hash = ?, anchor_timestamp = ?
                   WHERE tx_hash = ?""",
                (anchor_hash, anchor_timestamp, tx_hash)
            )
        await self._db.commit()

    async def get_latest_anchor(self) -> Optional[dict]:
        cursor = await self._db.execute(
            """SELECT root_hash, anchor_timestamp FROM anchor_records
               ORDER BY id DESC LIMIT 1"""
        )
        row = await cursor.fetchone()
        if row:
            return {"root_hash": row[0], "anchor_timestamp": row[1]}
        return None

    async def add_anchor_record(self, root_hash: str, transaction_count: int, gist_url: Optional[str],
                                 gist_commit_hash: Optional[str], anchor_timestamp: str, previous_anchor: Optional[str]) -> int:
        cursor = await self._db.execute(
            """INSERT INTO anchor_records (root_hash, transaction_count, gist_url, gist_commit_hash, anchor_timestamp, previous_anchor)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (root_hash, transaction_count, gist_url, gist_commit_hash, anchor_timestamp, previous_anchor)
        )
        await self._db.commit()
        return cursor.lastrowid

    async def get_all_transactions(self):
        cursor = await self._db.execute(
            """SELECT tx_hash, sender, receiver, amount, fee, timestamp, anchor_hash
               FROM transactions
               ORDER BY timestamp ASC"""
        )
        rows = await cursor.fetchall()
        return [
            {
                "tx_hash": row[0],
                "sender": row[1],
                "receiver": row[2],
                "amount": row[3],
                "fee": row[4],
                "timestamp": row[5],
                "anchor_hash": row[6]
            }
            for row in rows
        ]