import aiosqlite
import asyncio

async def check():
    db = await aiosqlite.connect('black2.db')
    
    # 检查deposits表字段
    cursor = await db.execute('PRAGMA table_info(deposits)')
    columns = await cursor.fetchall()
    print('Deposits表字段:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    # 检查users表
    cursor = await db.execute('SELECT COUNT(*) FROM users')
    count = await cursor.fetchone()
    print(f'\nUsers表记录数: {count[0]}')
    
    # 列出前3个用户
    cursor = await db.execute('SELECT id, address FROM users LIMIT 3')
    users = await cursor.fetchall()
    print('\n前3个用户:')
    for user in users:
        print(f'  ID: {user[0]}, Address: {user[1][:20]}...')
    
    await db.close()

asyncio.run(check())
