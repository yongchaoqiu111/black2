import aiosqlite
import asyncio

async def add_test_user():
    async with aiosqlite.connect('black2.db') as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (email, password_hash, address, is_verified) VALUES (?, ?, ?, 1)",
            ("test@ai.com", "hash", "TTestSellerAI123456789")
        )
        await db.commit()
        print("Test user added successfully.")

asyncio.run(add_test_user())
