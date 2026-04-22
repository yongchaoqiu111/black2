import sqlite3
conn = sqlite3.connect('black2.db')
c = conn.cursor()
c.execute('SELECT wallet_address, COUNT(*) as cnt FROM sub_wallets GROUP BY wallet_address')
rows = c.fetchall()
for r in rows:
    print(f'{r[1]} users share wallet: {r[0]}')
conn.close()
