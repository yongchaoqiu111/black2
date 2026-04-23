import aiosqlite
import asyncio

async def check_product_66():
    async with aiosqlite.connect('black2.db') as db:
        # Check products with price 66
        cursor = await db.execute('SELECT product_id, seller_address, name, price FROM products WHERE price = ?', (66,))
        products = await cursor.fetchall()
        
        print(f"--- Products with price 66 ({len(products)}) ---")
        for p in products:
            print(f"Product ID: {p[0]}")
            print(f"Seller Address: {p[1]}")
            print(f"Name: {p[2]}")
            print(f"Price: {p[3]}")
            
            # Find user by address
            cursor2 = await db.execute('SELECT address, email FROM users WHERE address = ?', (p[1],))
            user = await cursor2.fetchone()
            if user:
                print(f"Publisher Email: {user[1]}")
            else:
                print("Publisher not found in users table")
            print("---")

asyncio.run(check_product_66())
