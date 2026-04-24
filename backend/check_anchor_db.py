import aiosqlite
import asyncio

async def check_anchor_status():
    async with aiosqlite.connect('black2.db') as db:
        # 检查最近几笔交易的锚定状态
        cursor = await db.execute('SELECT tx_id, anchor_hash FROM transactions ORDER BY timestamp DESC LIMIT 5')
        rows = await cursor.fetchall()
        print("\n--- 交易锚定状态检查 ---")
        for row in rows:
            status = "已锚定" if row[1] else "待锚定"
            print(f"TX ID: {row[0]} - {status}")

if __name__ == "__main__":
    asyncio.run(check_anchor_status())
