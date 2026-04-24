import asyncio
import aiosqlite
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def migrate_add_ai_fields():
    async with aiosqlite.connect("black2.db") as db:
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in await cursor.fetchall()]
        
        if 'ai_address' not in columns:
            print("[Migration] Adding ai_address to users table...")
            await db.execute("ALTER TABLE users ADD COLUMN ai_address TEXT")
        
        if 'human_balance' not in columns:
            print("[Migration] Adding human_balance to users table...")
            await db.execute("ALTER TABLE users ADD COLUMN human_balance REAL DEFAULT 0.0")
            
        if 'ai_balance' not in columns:
            print("[Migration] Adding ai_balance to users table...")
            await db.execute("ALTER TABLE users ADD COLUMN ai_balance REAL DEFAULT 0.0")
            
        # Add wallet_type to sub_wallets if missing
        cursor = await db.execute("PRAGMA table_info(sub_wallets)")
        sub_columns = [row[1] for row in await cursor.fetchall()]
        if 'wallet_type' not in sub_columns:
            print("[Migration] Adding wallet_type to sub_wallets table...")
            await db.execute("ALTER TABLE sub_wallets ADD COLUMN wallet_type TEXT DEFAULT 'human'")

        await db.commit()
        print("✅ Database migration for AI Wallet completed.")

if __name__ == "__main__":
    asyncio.run(migrate_add_ai_fields())
