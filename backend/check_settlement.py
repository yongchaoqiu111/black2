import aiosqlite
import asyncio

async def check_settlement():
    async with aiosqlite.connect('black2.db') as db:
        # 1. Check last transaction
        cursor = await db.execute('SELECT tx_id, status, from_address, to_address, amount FROM transactions ORDER BY id DESC LIMIT 1')
        tx = await cursor.fetchone()
        if not tx:
            print("No transactions found")
            return
        
        print(f"--- Last Transaction ---")
        print(f"ID: {tx[0]}")
        print(f"Status: {tx[1]}")
        print(f"From (Buyer): {tx[2]}")
        print(f"To (Seller): {tx[3]}")
        print(f"Amount: {tx[4]} USDT")
        
        # 2. Check referral data
        cursor = await db.execute('SELECT * FROM transaction_referrals WHERE tx_id = ?', (tx[0],))
        referral = await cursor.fetchone()
        
        print(f"\n--- Referral Data ---")
        if referral:
            print(f"tu1: {referral[2]} -> {referral[3]} USDT")
            print(f"tu2: {referral[4]} -> {referral[5]} USDT")
            print(f"tu3: {referral[6]} -> {referral[7]} USDT")
            print(f"Settlement Status: {referral[8]}")
            
            # 3. Check wallet balances
            addresses = [addr for addr in [referral[2], referral[4], referral[6]] if addr]
            if addresses:
                placeholders = ','.join(['?' for _ in addresses])
                cursor = await db.execute(f'SELECT address, balance, total_earned FROM ai_wallets WHERE address IN ({placeholders})', addresses)
                wallets = await cursor.fetchall()
                
                print(f"\n--- Wallet Balances ---")
                for w in wallets:
                    print(f"{w[0]}:")
                    print(f"  Balance: {w[1]} USDT")
                    print(f"  Total Earned: {w[2]} USDT")
        else:
            print("No referral data found (Maybe settlement failed?)")

asyncio.run(check_settlement())
