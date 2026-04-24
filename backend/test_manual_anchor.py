import asyncio
from src.db.transaction_db import TransactionDB
from src.anchor.anchor_service import AnchorService

async def test_anchor():
    db = TransactionDB()
    svc = AnchorService(db)
    print("Starting manual anchor test...")
    r = await svc.perform_anchor()
    print("Result:", r)

if __name__ == "__main__":
    asyncio.run(test_anchor())
