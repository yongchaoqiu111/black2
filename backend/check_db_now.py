import aiosqlite
import asyncio

async def check_all_data():
    async with aiosqlite.connect('black2.db') as db:
        # Check Users
        cursor = await db.execute('SELECT address, ai_address FROM users')
        users = await cursor.fetchall()
        print(f"--- Users ({len(users)}) ---")
        for u in users:
            print(f"Addr: {u[0]}, AI: {u[1]}")

        # Check Products
        cursor = await db.execute('SELECT product_id, seller_address, name, price FROM products')
        products = await cursor.fetchall()
        print(f"\n--- Products ({len(products)}) ---")
        for p in products:
            print(f"ID: {p[0]}, Seller: {p[1]}, Name: {p[2]}, Price: {p[3]}")

asyncio.run(check_all_data())
