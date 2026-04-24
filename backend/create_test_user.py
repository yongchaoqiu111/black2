import asyncio
import hashlib
import aiosqlite
import sys
import os

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(__file__))

async def create_test_user():
    email = "test@black2.com"
    password = "123456"
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    address = "TTestUser" + hashlib.md5(email.encode()).hexdigest()[:8]
    
    async with aiosqlite.connect("black2.db") as db:
        # Insert user
        await db.execute('''
            INSERT OR IGNORE INTO users (email, address, password_hash, is_verified) 
            VALUES (?, ?, ?, 1)
        ''', (email, address, pwd_hash))
        
        # Check if AI wallet exists, if not create one
        cursor = await db.execute(
            'SELECT wallet_address FROM sub_wallets WHERE user_address = ?',
            (address,)
        )
        ai_row = await cursor.fetchone()
        
        if not ai_row:
            ai_address = "0x" + hashlib.sha256((address + "ai").encode()).hexdigest()[:40]
            private_key = hashlib.sha256((address + "private").encode()).hexdigest()
            await db.execute('''
                INSERT INTO sub_wallets (user_address, wallet_address, private_key)
                VALUES (?, ?, ?)
            ''', (address, ai_address, private_key))
            print(f"[Info] Created AI Wallet for test user: {ai_address}")
        
        await db.commit()
        print(f"✅ Test user created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Address: {address}")

if __name__ == "__main__":
    asyncio.run(create_test_user())
