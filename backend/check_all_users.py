import aiosqlite
import asyncio

async def check_all_users():
    async with aiosqlite.connect('black2.db') as db:
        cursor = await db.execute('SELECT address, tu1, tu2, tu3 FROM users')
        users = await cursor.fetchall()
        
        print(f"--- All Users ---")
        for u in users:
            print(f"Addr: {u[0]}, TU1: {u[1]}, TU2: {u[2]}, TU3: {u[3]}")

asyncio.run(check_all_users())
