import aiosqlite
import asyncio

async def check_completed():
    async with aiosqlite.connect('black2.db') as db:
        cursor = await db.execute('SELECT tx_id, status FROM transactions WHERE status = "completed" LIMIT 1')
        tx = await cursor.fetchone()
        if tx:
            print(f'Completed Order: {tx[0]}')
            cursor2 = await db.execute('SELECT * FROM transaction_referrals WHERE tx_id = ?', (tx[0],))
            ref = await cursor2.fetchone()
            if ref:
                print(f'tu1: {ref[2]} -> {ref[3]}')
                print(f'tu2: {ref[4]} -> {ref[5]}')
                print(f'tu3: {ref[6]} -> {ref[7]}')
                print(f'Settlement: {ref[8]}')
            else:
                print('No referral data')
        else:
            print('No completed orders')

asyncio.run(check_completed())
