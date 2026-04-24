"""
Database Migration Script

Adds X402 escrow fields to transactions table.
Run this script to migrate existing database to support X402 protocol.
"""

import asyncio
import aiosqlite
import os

DB_PATH = os.getenv('DB_PATH', 'black2.db')


async def migrate():
    """
    Add X402 escrow fields to transactions table.
    """
    print(f"[Migration] Starting migration on {DB_PATH}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if x402_escrow_id column exists
        cursor = await db.execute("PRAGMA table_info(transactions)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"[Migration] Current columns: {column_names}")
        
        # Add x402_escrow_id if not exists
        if 'x402_escrow_id' not in column_names:
            await db.execute('''
                ALTER TABLE transactions
                ADD COLUMN x402_escrow_id TEXT
            ''')
            print("[Migration] Added x402_escrow_id column")
        
        if 'x402_escrow_address' not in column_names:
            await db.execute('''
                ALTER TABLE transactions
                ADD COLUMN x402_escrow_address TEXT
            ''')
            print("[Migration] Added x402_escrow_address column")
        
        if 'x402_status' not in column_names:
            await db.execute('''
                ALTER TABLE transactions
                ADD COLUMN x402_status TEXT DEFAULT 'none'
            ''')
            print("[Migration] Added x402_status column")
        
        # Create x402_transactions table for tracking X402 specific transactions
        await db.execute('''
            CREATE TABLE IF NOT EXISTS x402_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                escrow_id TEXT UNIQUE NOT NULL,
                escrow_address TEXT NOT NULL,
                sender_address TEXT NOT NULL,
                receiver_address TEXT NOT NULL,
                amount REAL NOT NULL,
                asset TEXT DEFAULT 'USDT',
                status TEXT DEFAULT 'pending',
                verdict TEXT,
                release_tx_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                released_at DATETIME
            )
        ''')
        print("[Migration] Created x402_transactions table")
        
        await db.commit()
        
        print("[Migration] Migration completed successfully")
        
        # Verify columns
        cursor = await db.execute("PRAGMA table_info(transactions)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"[Migration] Final columns: {column_names}")


if __name__ == "__main__":
    asyncio.run(migrate())
