import sqlite3
conn = sqlite3.connect('black2.db')
c = conn.cursor()

# Check if wallet_type column exists
c.execute('PRAGMA table_info(sub_wallets)')
columns = [col[1] for col in c.fetchall()]

if 'wallet_type' not in columns:
    print('Adding wallet_type column...')
    c.execute('ALTER TABLE sub_wallets ADD COLUMN wallet_type TEXT DEFAULT "human"')
    conn.commit()
    print('Column added successfully')
else:
    print('wallet_type column already exists')

conn.close()
