import aiosqlite
import asyncio

async def check_tables():
    async with aiosqlite.connect('black2.db') as db:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await cursor.fetchall()
        print("Tables in database:", [t[0] for t in tables])
        
        if 'arbitration_fund_pool' in [t[0] for t in tables]:
            print("✅ arbitration_fund_pool table exists.")
            cursor = await db.execute("PRAGMA table_info(arbitration_fund_pool)")
            cols = await cursor.fetchall()
            for col in cols:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ arbitration_fund_pool table NOT found.")

asyncio.run(check_tables())
