import aiosqlite
import asyncio

async def reset_db():
    async with aiosqlite.connect('black2.db') as db:
        # Delete all transactions and related data
        await db.execute('DELETE FROM transaction_referrals')
        await db.execute('DELETE FROM transactions')
        
        # Delete all products and contracts
        await db.execute('DELETE FROM contracts')
        await db.execute('DELETE FROM products')
        
        # Delete all users and wallets
        await db.execute('DELETE FROM users')
        await db.execute('DELETE FROM ai_wallets')
        await db.execute('DELETE FROM human_wallets')
        
        # Reset auto-increment counters (if applicable)
        await db.execute('DELETE FROM sqlite_sequence WHERE name IN ("users", "transactions")')
        
        await db.commit()
        print("Database has been fully reset. All users, wallets, and orders are cleared.")

asyncio.run(reset_db())
