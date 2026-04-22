import sqlite3

conn = sqlite3.connect(r'F:\black2\backend\black2.db')
c = conn.cursor()

# 检查sub_wallets表所有记录
print('=== sub_wallets表 ===')
c.execute('SELECT user_address, wallet_address FROM sub_wallets')
wallets = c.fetchall()
print(f'共{len(wallets)}条记录')
for w in wallets:
    print(f'  User: {w[0][:30]}...' if w[0] else '  User: None')
    print(f'  Wallet: {w[1]}')
    print()

# 检查wallet_address是否唯一
print('\n=== 地址唯一性检查 ===')
c.execute('SELECT COUNT(DISTINCT wallet_address) FROM sub_wallets')
unique_wallets = c.fetchone()[0]
print(f'唯一的钱包地址数: {unique_wallets}')

if unique_wallets == 1:
    c.execute('SELECT wallet_address FROM sub_wallets LIMIT 1')
    addr = c.fetchone()[0]
    print(f'所有用户共用地址: {addr}')
elif unique_wallets > 1:
    c.execute('SELECT DISTINCT wallet_address FROM sub_wallets')
    addrs = c.fetchall()
    print(f'不同地址:')
    for a in addrs:
        print(f'  - {a[0]}')

conn.close()
