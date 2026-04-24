import sqlite3

conn = sqlite3.connect('black2.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

if ('arbitration_fund_pool',) in tables:
    print("✅ Table exists!")
else:
    print("❌ Table missing. Running migration...")
    from src.db.transaction_db import init_db
    import asyncio
    asyncio.run(init_db())
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables after migration:", cursor.fetchall())

conn.close()
