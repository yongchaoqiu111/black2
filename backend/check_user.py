import sqlite3
conn = sqlite3.connect('black2.db')
c = conn.cursor()

target = 'TPbr2Fa'

print('=== Users table ===')
c.execute('SELECT address, email FROM users WHERE address LIKE ?', (f'%{target}%',))
print(c.fetchall())

print('=== Sub wallets ===')
c.execute('SELECT user_address, wallet_address FROM sub_wallets WHERE wallet_address LIKE ?', (f'%{target}%',))
rows = c.fetchall()
print(rows)

print('=== Human wallets ===')
c.execute('SELECT address FROM human_wallets WHERE address LIKE ?', (f'%{target}%',))
print(c.fetchall())

conn.close()
