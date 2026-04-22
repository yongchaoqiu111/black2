import sqlite3
conn = sqlite3.connect('black2.db')
c = conn.cursor()

# 检查 sub_wallets 表
print("=== Sub-wallets 表数据 ===")
c.execute("SELECT user_address, wallet_address FROM sub_wallets")
rows = c.fetchall()

if not rows:
    print("表为空！")
else:
    print(f"共 {len(rows)} 条记录:\n")
    for i, (user_addr, wallet_addr) in enumerate(rows, 1):
        print(f"记录 {i}:")
        print(f"  User Address: {user_addr[:20]}...")
        print(f"  Wallet Address: {wallet_addr}")
        print()

# 检查是否有重复的 wallet_address
print("\n=== 地址重复检查 ===")
c.execute("SELECT wallet_address, COUNT(*) as cnt FROM sub_wallets GROUP BY wallet_address HAVING cnt > 1")
duplicates = c.fetchall()

if duplicates:
    print(f"发现 {len(duplicates)} 个重复地址:")
    for wallet_addr, cnt in duplicates:
        print(f"  {wallet_addr} 被 {cnt} 个用户使用")
        
        # 显示使用这个地址的所有用户
        c.execute("SELECT user_address FROM sub_wallets WHERE wallet_address = ?", (wallet_addr,))
        users = c.fetchall()
        for u in users:
            print(f"    - {u[0][:30]}...")
else:
    print("没有发现重复地址")

conn.close()
