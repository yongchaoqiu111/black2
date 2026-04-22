import sqlite3
conn = sqlite3.connect('black2.db')
c = conn.cursor()
c.execute('PRAGMA table_info(sub_wallets)')
columns = c.fetchall()
print('sub_wallets columns:')
for col in columns:
    print(f"  {col[1]} ({col[2]})")
conn.close()
