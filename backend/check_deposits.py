import sqlite3

conn = sqlite3.connect('black2.db')
c = conn.cursor()

print("=== 充值记录 ===\n")
c.execute('''SELECT id, user_address, wallet_address, amount, status, created_at 
             FROM deposits 
             ORDER BY id DESC LIMIT 10''')
deposits = c.fetchall()

if deposits:
    for d in deposits:
        print(f"充值ID: {d[0]}")
        print(f"  用户地址: {d[1]}")
        print(f"  钱包地址: {d[2]}")
        print(f"  金额: {d[3]}")
        print(f"  状态: {d[4]}")
        print(f"  时间: {d[5]}")
        print()
else:
    print("没有充值记录\n")

print("\n=== 用户余额 ===\n")
c.execute('SELECT email, address, ai_address, human_balance, ai_balance FROM users ORDER BY id DESC LIMIT 5')
users = c.fetchall()
for u in users:
    print(f"邮箱: {u[0]}")
    print(f"  人类钱包: {u[1][:20]}...")
    print(f"  AI钱包: {u[2][:20]}...")
    print(f"  人类余额: {u[3]}")
    print(f"  AI余额: {u[4]}")
    print()

conn.close()
