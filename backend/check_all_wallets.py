import aiosqlite
import asyncio

async def check_all():
    async with aiosqlite.connect('black2.db') as db:
        # Check all wallets
        cursor = await db.execute('SELECT address, balance FROM ai_wallets')
        wallets = await cursor.fetchall()
        print(f"--- All AI Wallets ---")
        for w in wallets:
            print(f"{w[0]}: {w[1]} USDT")

        # Check transaction details
        cursor = await db.execute('SELECT * FROM transactions WHERE tx_id = ?', ('856e02e7-6262-4488-8200-9f3622c5725f',))
        tx = await cursor.fetchone()
        print(f"\n--- Transaction Details ---")
        if tx:
            print(f"ID: {tx[0]}")
            print(f"From: {tx[1]}")
            print(f"To: {tx[2]}")
            print(f"Amount: {tx[3]}")
            print(f"Status: {tx[7]}")
        else:
            print("Transaction not found")

asyncio.run(check_all())
