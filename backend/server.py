"""
Black2 Main Server

Main entry point for the Black2 clearing API service.
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Optional

# Import modules
from src.api.routes import router as api_router
from src.db.transaction_db import init_db, get_transaction, update_transaction_status
from src.agents.arbitrator import Arbitrator
from src.anchor.anchor_service import AnchorService
from src.anchor.scheduler import AnchorScheduler
from src.db.transaction_db import TransactionDB as CoreDB

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Black2 Clearing Protocol",
    description="Unified API for transaction clearing, anchoring, and arbitration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)

# Global instances
core_db: CoreDB = None
anchor_scheduler: AnchorScheduler = None

class DisputeRequest(BaseModel):
    reason: Optional[str] = "Hash mismatch or non-delivery"

@app.on_event("startup")
async def startup_event():
    global core_db, anchor_scheduler
    
    # Initialize Core DB (1号员工)
    await init_db()
    core_db = CoreDB(os.getenv("DB_PATH", "./black2.db"))
    
    # Initialize Anchor Service (2号员工)
    anchor_service = AnchorService(core_db)
    interval = int(os.getenv("ANCHOR_INTERVAL_HOURS", "1"))
    anchor_scheduler = AnchorScheduler(anchor_service, interval)
    anchor_scheduler.start()
    
    print("Black2 System Started: API + Anchoring + Arbitration")

@app.on_event("shutdown")
async def shutdown_event():
    if anchor_scheduler:
        await anchor_scheduler.stop()

@app.post("/api/v1/transactions/{tx_id}/dispute")
async def create_dispute(tx_id: str, request: DisputeRequest):
    """
    Initiate a dispute for a transaction.
    Integrates 4号 employee's Arbitrator.
    """
    tx = await get_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if tx['status'] != 'delivered' and tx['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Transaction cannot be disputed in current status")

    # Trigger Arbitration (4号员工)
    arbitrator = Arbitrator()
    result = arbitrator.arbitrate(tx_id, tx['contract_hash'], tx.get('file_hash'))
    
    # Update status based on verdict
    new_status = 'refunded' if result['verdict'] == 'buyer_wins' else 'completed'
    await update_transaction_status(tx_id, new_status)
    
    return {
        "tx_id": tx_id,
        "arbitration_result": result,
        "new_status": new_status,
        "reason": request.reason
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
