import aiosqlite
import asyncio

async def check_reputation():
    async with aiosqlite.connect('black2.db') as db:
        # 检查卖家和买家的信誉分及仲裁次数
        cursor = await db.execute(
            'SELECT address, reputation_score, dispute_count FROM users WHERE address IN (?, ?)',
            ("TTestSellerAI123456789", "TBuyerAI987654321")
        )
        rows = await cursor.fetchall()
        print("\n--- 信誉系统状态检查 ---")
        for row in rows:
            print(f"Address: {row[0]}")
            print(f"  Reputation Score: {row[1]}")
            print(f"  Dispute Count: {row[2]}")
            # 计算摩擦系数 (Dispute / Total Transactions * 100)
            # 注意：friction_index 是动态计算的，这里我们看原始数据
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(check_reputation())
