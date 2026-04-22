import sqlite3
conn = sqlite3.connect('black2.db')
c = conn.cursor()

# Check current users table structure
c.execute('PRAGMA table_info(users)')
columns = [col[1] for col in c.fetchall()]
print('Current users columns:', columns)

# Add new columns if not exist
new_columns = {
    'ai_address': 'TEXT',
    'human_balance': 'REAL DEFAULT 0.0',
    'ai_balance': 'REAL DEFAULT 0.0',
    'tu1': 'TEXT',
    'tu2': 'TEXT',
    'tu3': 'TEXT'
}

for col_name, col_type in new_columns.items():
    if col_name not in columns:
        print(f'Adding {col_name}...')
        try:
            c.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}')
            print(f'  ✓ {col_name} added')
        except Exception as e:
            print(f'  ✗ {col_name} error: {e}')
    else:
        print(f'  - {col_name} already exists')

conn.commit()
conn.close()
print('\nMigration completed!')
