import sqlite3

conn = sqlite3.connect('black2.db')
c = conn.cursor()

print("=== 用户 111, 112, 113 的关系 ===\n")

# 查这三个用户的基本信息
c.execute('''SELECT id, email, address, ai_address, tu1, tu2, tu3 
             FROM users 
             WHERE email LIKE '%111%' OR email LIKE '%112%' OR email LIKE '%113%'
             ORDER BY id''')

users = c.fetchall()

for u in users:
    print(f"用户ID: {u[0]}, 邮箱: {u[1]}")
    print(f"  人类钱包: {u[2]}")
    print(f"  AI钱包: {u[3]}")
    print(f"  tu1 (第一代): {u[4]}")
    print(f"  tu2 (第二代): {u[5]}")
    print(f"  tu3 (第三代): {u[6]}")
    print()

print("\n=== 所有用户的三代关系概览 ===\n")
c.execute('SELECT id, email, ai_address, tu1, tu2, tu3 FROM users ORDER BY id')
all_users = c.fetchall()

for u in all_users:
    if u[3] or u[4] or u[5]:  # 只要有推荐关系就显示
        print(f"用户 {u[1]} (AI: {u[2][:20]}...)")
        print(f"  → tu1: {u[3][:20] if u[3] else '无'}...")
        print(f"  → tu2: {u[4][:20] if u[4] else '无'}...")
        print(f"  → tu3: {u[5][:20] if u[5] else '无'}...")
        print()

conn.close()
