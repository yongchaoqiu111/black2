import asyncio
import aiosqlite

async def topup_ai_wallet():
    address = 'TGmNWoN5bRwf1rpcr4MbojTvdHyC2vh5jf'
    amount = 1000.0
    
    async with aiosqlite.connect('black2.db') as db:
        # Update both tables
        await db.execute(
            'UPDATE users SET ai_balance = ai_balance + ? WHERE ai_address = ?',
            (amount, address)
        )
        await db.execute(
            'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
            (amount, address)
        )
        await db.commit()
        
        # Verify
        cursor = await db.execute(
            'SELECT balance FROM ai_wallets WHERE address = ?',
            (address,)
        )
        result = await cursor.fetchone()
        print(f'✅ AI wallet {address} topped up to {result[0]} USDT')

asyncio.run(topup_ai_wallet())
