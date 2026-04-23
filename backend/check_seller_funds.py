import aiosqlite
import asyncio

async def check_wallets():
    async with aiosqlite.connect('black2.db') as db:
        # Check seller wallet
        cursor = await db.execute('SELECT address, balance, total_earned FROM ai_wallets WHERE address = ?', ('TN8qJz7K3V9pL2xR5wM4nB6cY1dF3gH8jK',))
        seller = await cursor.fetchone()
        print(f"--- Seller Wallet ---")
        if seller:
            print(f"Address: {seller[0]}")
            print(f"Balance: {seller[1]} USDT")
            print(f"Total Earned: {seller[2]} USDT")
        else:
            print("Seller wallet not found")

        # Check transaction_referrals table
        cursor = await db.execute('SELECT * FROM transaction_referrals WHERE tx_id = ?', ('856e02e7-6262-4488-8200-9f3622c5725f',))
        ref = await cursor.fetchone()
        print(f"\n--- Referral Data ---")
        if ref:
            print(f"ID: {ref[0]}")
            print(f"TX ID: {ref[1]}")
            print(f"TU1: {ref[2]} -> {ref[3]}")
            print(f"TU2: {ref[4]} -> {ref[5]}")
            print(f"TU3: {ref[6]} -> {ref[7]}")
            print(f"Status: {ref[8]}")
        else:
            print("No referral record found in transaction_referrals table")

asyncio.run(check_wallets())
