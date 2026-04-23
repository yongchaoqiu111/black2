import aiosqlite
import asyncio

async def check_users():
    async with aiosqlite.connect('black2.db') as db:
        cursor = await db.execute('SELECT address, tu1, tu2, tu3 FROM users WHERE address = ?', ('TN8qJz7K3V9pL2xR5wM4nB6cY1dF3gH8jK',))
        seller = await cursor.fetchone()
        
        print(f"--- Seller User Info ---")
        if seller:
            print(f"Address: {seller[0]}")
            print(f"TU1: {seller[1]}")
            print(f"TU2: {seller[2]}")
            print(f"TU3: {seller[3]}")
        else:
            print("Seller not found in users table")

asyncio.run(check_users())
