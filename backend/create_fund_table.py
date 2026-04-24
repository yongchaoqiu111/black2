import sqlite3

try:
    conn = sqlite3.connect('black2.db')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='arbitration_fund_pool'")
    result = cursor.fetchone()
    
    if result:
        print("✅ arbitration_fund_pool 表已存在！")
        cursor.execute("PRAGMA table_info(arbitration_fund_pool)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("❌ 表不存在，正在创建...")
        cursor.execute('''
            CREATE TABLE arbitration_fund_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                source_tx_id TEXT,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("✅ 表创建成功！")
        
except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    conn.close()
