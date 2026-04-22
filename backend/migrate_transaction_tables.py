"""
数据库迁移脚本：将分润字段从 transactions 表迁移到 transaction_referrals 表

执行方式：
py migrate_transaction_tables.py
"""

import asyncio
import aiosqlite

DB_PATH = 'black2.db'


async def migrate():
    print("开始迁移交易表结构...")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # 1. 创建 transaction_referrals 表
        print("1. 创建 transaction_referrals 表...")
        await db.execute('''
            CREATE TABLE IF NOT EXISTS transaction_referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT UNIQUE NOT NULL,
                tu1_address TEXT,
                tu1_amount REAL DEFAULT 0,
                tu2_address TEXT,
                tu2_amount REAL DEFAULT 0,
                tu3_address TEXT,
                tu3_amount REAL DEFAULT 0,
                settlement_status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                settled_at DATETIME,
                FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
            )
        ''')
        
        # 2. 创建 transaction_arbitrations 表
        print("2. 创建 transaction_arbitrations 表...")
        await db.execute('''
            CREATE TABLE IF NOT EXISTS transaction_arbitrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT UNIQUE NOT NULL,
                dispute_reason TEXT,
                verdict TEXT,
                arbitration_result TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME,
                FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
            )
        ''')
        
        # 3. 迁移现有数据（如果有）
        print("3. 迁移现有分润数据...")
        cursor = await db.execute('''
            SELECT tx_id, tu1_address, tu1_amount, tu2_address, tu2_amount, 
                   tu3_address, tu3_amount, settlement_status
            FROM transactions
            WHERE tu1_address IS NOT NULL OR tu2_address IS NOT NULL OR tu3_address IS NOT NULL
        ''')
        
        rows = await cursor.fetchall()
        migrated_count = 0
        
        for row in rows:
            tx_id, tu1_addr, tu1_amt, tu2_addr, tu2_amt, tu3_addr, tu3_amt, status = row
            
            await db.execute('''
                INSERT OR IGNORE INTO transaction_referrals 
                (tx_id, tu1_address, tu1_amount, tu2_address, tu2_amount, 
                 tu3_address, tu3_amount, settlement_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tx_id, tu1_addr, tu1_amt, tu2_addr, tu2_amt, tu3_addr, tu3_amt, status or 'pending'))
            
            migrated_count += 1
        
        print(f"   迁移了 {migrated_count} 条分润记录")
        
        # 4. 删除 transactions 表中的分润字段（可选，先保留以兼容）
        # SQLite 不支持 DROP COLUMN，需要重建表
        # 暂时不删除，等确认新表工作正常后再清理
        
        await db.commit()
        
        print("✅ 迁移完成！")
        print("\n表结构说明：")
        print("- transactions: 订单基础信息")
        print("- transaction_referrals: 三代分润信息")
        print("- transaction_arbitrations: 仲裁记录")


if __name__ == '__main__':
    asyncio.run(migrate())
