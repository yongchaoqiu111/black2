import sqlite3
conn = sqlite3.connect('black2.db')
c = conn.cursor()

# Check current transactions table structure
c.execute('PRAGMA table_info(transactions)')
columns = [col[1] for col in c.fetchall()]
print('Current transactions columns:', columns)

# Add settlement fields
new_columns = {
    'tu1_address': 'TEXT',
    'tu1_amount': 'REAL DEFAULT 0.0',
    'tu2_address': 'TEXT',
    'tu2_amount': 'REAL DEFAULT 0.0',
    'tu3_address': 'TEXT',
    'tu3_amount': 'REAL DEFAULT 0.0',
    'settlement_status': "TEXT DEFAULT 'pending'"  # pending, processing, completed, failed
}

for col_name, col_type in new_columns.items():
    if col_name not in columns:
        print(f'Adding {col_name}...')
        try:
            c.execute(f'ALTER TABLE transactions ADD COLUMN {col_name} {col_type}')
            print(f'  ✓ {col_name} added')
        except Exception as e:
            print(f'  ✗ {col_name} error: {e}')
    else:
        print(f'  - {col_name} already exists')

conn.commit()
conn.close()
print('\nTransactions table migration completed!')
