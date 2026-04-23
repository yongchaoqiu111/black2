import aiosqlite
import asyncio

async def count_users():
    async with aiosqlite.connect('black2.db') as db:
        cursor = await db.execute('SELECT COUNT(*) FROM users')
        count = await cursor.fetchone()
        print(f'Total users in database: {count[0]}')

asyncio.run(count_users())
