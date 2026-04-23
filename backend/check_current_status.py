import aiosqlite
import asyncio

async def check_new_data():
    async with aiosqlite.connect('black2.db') as db:
        # Check Users
        cursor = await db.execute('SELECT address, ai_address, tu1, tu2, tu3 FROM users')
        users = await cursor.fetchall()
        print(f"--- Users ({len(users)}) ---")
        for u in users:
            print(f"Addr: {u[0]}, AI: {u[1]}, TU1: {u[2]}, TU2: {u[3]}, TU3: {u[4]}")

        # Check Products
        cursor = await db.execute('SELECT product_id, seller_address, name, price FROM products')
        products = await cursor.fetchall()
        print(f"\n--- Products ({len(products)}) ---")
        for p in products:
            print(f"ID: {p[0]}, Seller: {p[1]}, Name: {p[2]}, Price: {p[3]}")

        # Check Transactions
        cursor = await db.execute('SELECT tx_id, from_address, to_address, amount, status FROM transactions')
        txs = await cursor.fetchall()
        print(f"\n--- Transactions ({len(txs)}) ---")
        for t in txs:
            print(f"TX: {t[0]}, From: {t[1]}, To: {t[2]}, Amount: {t[3]}, Status: {t[4]}")

        # Check Referrals
        cursor = await db.execute('SELECT tx_id, tu1_address, tu1_amount, settlement_status FROM transaction_referrals')
        refs = await cursor.fetchall()
        print(f"\n--- Referrals ({len(refs)}) ---")
        for r in refs:
            print(f"TX: {r[0]}, TU1: {r[1]} ({r[2]}), Status: {r[3]}")

asyncio.run(check_new_data())
