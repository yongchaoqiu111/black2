import aiosqlite
import asyncio

async def check_tx_detail():
    async with aiosqlite.connect('black2.db') as db:
        cursor = await db.execute('SELECT * FROM transactions WHERE tx_id = ?', ('856e02e7-6262-4488-8200-9f3622c5725f',))
        columns = [description[0] for description in cursor.description]
        tx = await cursor.fetchone()
        
        print(f"--- Transaction Columns ---")
        print(columns)
        print(f"\n--- Transaction Data ---")
        if tx:
            for i, col in enumerate(columns):
                print(f"{col}: {tx[i]}")
        else:
            print("Transaction not found")

asyncio.run(check_tx_detail())
