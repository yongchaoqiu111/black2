import sqlite3

conn = sqlite3.connect('black2.db')
c = conn.cursor()

# Get all column names
c.execute('PRAGMA table_info(transactions)')
columns = [col[1] for col in c.fetchall()]
print("Available columns:", columns)
print()

# Get last 3 transactions
c.execute('SELECT * FROM transactions ORDER BY rowid DESC LIMIT 3')
rows = c.fetchall()

for i, row in enumerate(rows, 1):
    print(f"=== Transaction {i} ===")
    for col, val in zip(columns, row):
        if col in ['tx_id', 'from_address', 'to_address']:
            print(f"  {col}: {str(val)[:30]}...")
        else:
            print(f"  {col}: {val}")
    print()

conn.close()
