"""
Transaction Database Module

Provides database operations for transaction records and anchor tracking.
"""

import aiosqlite
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


class TransactionDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)
        
        # Transactions table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT UNIQUE NOT NULL,
                tx_hash TEXT UNIQUE NOT NULL,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount REAL NOT NULL,
                fee REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                contract_hash TEXT,
                file_hash TEXT,
                escrow_id TEXT,
                anchor_hash TEXT,
                anchor_timestamp TEXT,
                x402_tx_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Anchor records table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS anchor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anchor_type TEXT NOT NULL,
                root_hash TEXT,
                transaction_count INTEGER,
                github_commit_hash TEXT,
                github_commit_url TEXT,
                x402_tx_hash TEXT,
                x402_chain_id INTEGER,
                anchor_timestamp TEXT NOT NULL,
                success INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Arbitration records table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS arbitration_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                verdict TEXT,
                verdict_reason TEXT,
                deadline TEXT,
                resolved_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # AI Wallets table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS ai_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                balance REAL NOT NULL DEFAULT 0.0,
                total_received REAL NOT NULL DEFAULT 0.0,
                total_refunded REAL NOT NULL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Users table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                reputation_score REAL NOT NULL DEFAULT 100.0,
                dispute_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transaction referrals table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS transaction_referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT NOT NULL,
                referrer_address TEXT NOT NULL,
                referral_amount REAL NOT NULL,
                settlement_status TEXT NOT NULL DEFAULT 'pending',
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

    async def get_unanchored_transactions(self, limit: Optional[int] = None) -> List[Dict]:
        if limit:
            cursor = await self._db.execute(
                """SELECT tx_hash, sender, receiver, amount, fee, timestamp
                   FROM transactions
                   WHERE anchor_hash IS NULL
                   ORDER BY timestamp ASC
                   LIMIT ?""",
                (limit,)
            )
        else:
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

    async def anchor_transactions(self, tx_hashes: List[str], anchor_hash: str, anchor_timestamp: str, x402_tx_hash: Optional[str] = None):
        for tx_hash in tx_hashes:
            await self._db.execute(
                """UPDATE transactions
                   SET anchor_hash = ?, anchor_timestamp = ?, x402_tx_hash = ?
                   WHERE tx_hash = ?""",
                (anchor_hash, anchor_timestamp, x402_tx_hash, tx_hash)
            )
        await self._db.commit()

    async def add_anchor_record(self, anchor_type: str, root_hash: Optional[str], transaction_count: Optional[int],
                                 github_commit_hash: Optional[str], github_commit_url: Optional[str],
                                 x402_tx_hash: Optional[str], x402_chain_id: Optional[int],
                                 anchor_timestamp: str, success: bool, error_message: Optional[str] = None) -> int:
        cursor = await self._db.execute(
            """INSERT INTO anchor_records (
               anchor_type, root_hash, transaction_count, github_commit_hash, github_commit_url,
               x402_tx_hash, x402_chain_id, anchor_timestamp, success, error_message
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (anchor_type, root_hash, transaction_count, github_commit_hash, github_commit_url,
             x402_tx_hash, x402_chain_id, anchor_timestamp, 1 if success else 0, error_message)
        )
        await self._db.commit()
        return cursor.lastrowid

    async def add_arbitration(self, arbitration_id: str, verdict: str, metadata: Optional[Dict],
                              github_commit_hash: Optional[str], x402_tx_hash: Optional[str]) -> int:
        cursor = await self._db.execute(
            """INSERT INTO arbitrations (arbitration_id, verdict, metadata, github_commit_hash, x402_tx_hash)
               VALUES (?, ?, ?, ?, ?)""",
            (arbitration_id, verdict, str(metadata) if metadata else None, github_commit_hash, x402_tx_hash)
        )
        await self._db.commit()
        return cursor.lastrowid

    async def get_latest_anchor(self, anchor_type: Optional[str] = None) -> Optional[Dict]:
        if anchor_type:
            cursor = await self._db.execute(
                """SELECT root_hash, anchor_timestamp, x402_tx_hash, github_commit_hash
                   FROM anchor_records
                   WHERE anchor_type = ? AND success = 1
                   ORDER BY id DESC LIMIT 1""",
                (anchor_type,)
            )
        else:
            cursor = await self._db.execute(
                """SELECT root_hash, anchor_timestamp, x402_tx_hash, github_commit_hash
                   FROM anchor_records
                   WHERE success = 1
                   ORDER BY id DESC LIMIT 1"""
            )
        row = await cursor.fetchone()
        if row:
            return {
                "root_hash": row[0],
                "anchor_timestamp": row[1],
                "x402_tx_hash": row[2],
                "github_commit_hash": row[3]
            }
        return None

    async def get_all_transactions(self, limit: Optional[int] = None) -> List[Dict]:
        if limit:
            cursor = await self._db.execute(
                """SELECT tx_hash, sender, receiver, amount, fee, timestamp, anchor_hash, x402_tx_hash
                   FROM transactions
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (limit,)
            )
        else:
            cursor = await self._db.execute(
                """SELECT tx_hash, sender, receiver, amount, fee, timestamp, anchor_hash, x402_tx_hash
                   FROM transactions
                   ORDER BY timestamp DESC"""
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
                "anchor_hash": row[6],
                "x402_tx_hash": row[7]
            }
            for row in rows
        ]

    async def get_anchor_stats(self) -> Dict[str, Any]:
        cursor = await self._db.execute(
            """SELECT COUNT(*) FROM transactions WHERE anchor_hash IS NOT NULL"""
        )
        anchored_count = (await cursor.fetchone())[0]
        
        cursor = await self._db.execute(
            """SELECT COUNT(*) FROM transactions WHERE anchor_hash IS NULL"""
        )
        unanchored_count = (await cursor.fetchone())[0]
        
        cursor = await self._db.execute(
            """SELECT COUNT(*) FROM anchor_records WHERE success = 1"""
        )
        successful_anchors = (await cursor.fetchone())[0]
        
        cursor = await self._db.execute(
            """SELECT COUNT(*) FROM anchor_records WHERE success = 0"""
        )
        failed_anchors = (await cursor.fetchone())[0]
        
        cursor = await self._db.execute(
            """SELECT COUNT(*) FROM arbitration_records"""
        )
        arbitration_count = (await cursor.fetchone())[0]
        
        return {
            "total_transactions": anchored_count + unanchored_count,
            "anchored_transactions": anchored_count,
            "unanchored_transactions": unanchored_count,
            "successful_anchors": successful_anchors,
            "failed_anchors": failed_anchors,
            "arbitration_count": arbitration_count
        }


async def settle_referral_rewards(tx_id: str, db_conn: Optional[aiosqlite.Connection] = None):
    """
    Settle referral rewards for a transaction.
    Can be called with an existing database connection or create a new one.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    should_close = False
    if db_conn is None:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        db_path = os.getenv("DB_PATH", "./backend/data/clearing.db")
        db_conn = await aiosqlite.connect(db_path)
        should_close = True
    
    try:
        # Get referral record
        cursor = await db_conn.execute(
            """SELECT referrer_address, referral_amount FROM transaction_referrals WHERE tx_id = ?""",
            (tx_id,)
        )
        referral = await cursor.fetchone()
        
        if referral:
            referrer, amount = referral
            
            # Credit referrer's wallet
            await db_conn.execute(
                """UPDATE ai_wallets SET balance = balance + ?, total_received = total_received + ? WHERE address = ?""",
                (amount, amount, referrer)
            )
            
            # Mark referral as settled
            await db_conn.execute(
                """UPDATE transaction_referrals SET settlement_status = 'settled' WHERE tx_id = ?""",
                (tx_id,)
            )
            
            logger.info(f"[Referral] Settled {amount} for tx {tx_id} to {referrer}")
            
        if db_conn:
            await db_conn.commit()
            
    except Exception as e:
        logger.error(f"[Referral] Failed to settle for tx {tx_id}: {e}", exc_info=True)
        if db_conn:
            await db_conn.rollback()
        raise
    finally:
        if should_close and db_conn:
            await db_conn.close()