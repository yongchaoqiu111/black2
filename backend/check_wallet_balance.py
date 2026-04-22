import asyncio
import aiosqlite

async def check_wallet():
    address = 'TGmNWoN5bRwf1rpcr4MbojTvdHyC2vh5jf'
    
    async with aiosqlite.connect('black2.db') as db:
        # Check human wallet
        cursor = await db.execute(
            'SELECT address, points_balance, locked_points, total_deposited FROM human_wallets WHERE address = ?',
            (address,)
        )
        result = await cursor.fetchone()
        print('Human Wallet:', result)
        
        # Check AI wallet
        cursor2 = await db.execute(
            'SELECT address, balance, total_earned FROM ai_wallets WHERE address = ?',
            (address,)
        )
        result2 = await cursor2.fetchone()
        print('AI Wallet:', result2)
        
        # Check deposits
        cursor3 = await db.execute(
            'SELECT id, user_address, amount, status, created_at FROM deposits WHERE user_address = ? ORDER BY created_at DESC LIMIT 5',
            (address,)
        )
        results3 = await cursor3.fetchall()
        print('Recent Deposits:')
        for row in results3:
            print(f'  {row}')

asyncio.run(check_wallet())
