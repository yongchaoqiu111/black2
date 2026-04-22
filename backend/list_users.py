import aiosqlite
import asyncio

async def check():
    db = await aiosqlite.connect('black2.db')
    
    # 查找特定地址
    target = 'TTbERTqEaRThMhy86SAvd9p5pgGzsuHo17'
    
    # 检查users表
    print('=== 检查 users 表 ===')
    cursor = await db.execute('SELECT id, address FROM users WHERE address = ?', (target,))
    result = await cursor.fetchone()
    if result:
        print(f'✓ 在 users 表中找到: ID={result[0]}, Address={result[1]}')
    else:
        print(f'✗ 在 users 表中未找到该地址')
    
    # 检查sub_wallets表
    print('\n=== 检查 sub_wallets 表 ===')
    cursor = await db.execute('SELECT user_address, wallet_address FROM sub_wallets WHERE wallet_address = ?', (target,))
    result = await cursor.fetchone()
    if result:
        print(f'✓ 在 sub_wallets 表中找到: UserAddress={result[0][:20]}..., WalletAddress={result[1][:20]}...')
    else:
        print(f'✗ 在 sub_wallets 表中未找到该地址')
    
    # 列出所有用户及其子钱包
    print('\n=== 所有用户及子钱包 ===')
    cursor = await db.execute('''
        SELECT u.id, u.address, sw.wallet_address 
        FROM users u 
        LEFT JOIN sub_wallets sw ON u.address = sw.user_address
    ''')
    rows = await cursor.fetchall()
    for row in rows:
        print(f'  User ID: {row[0]}')
        print(f'    User Address: {row[1][:20]}...' if row[1] else '    User Address: None')
        print(f'    Wallet Address: {row[2][:20]}...' if row[2] else '    Wallet Address: None')
    
    await db.close()

asyncio.run(check())
