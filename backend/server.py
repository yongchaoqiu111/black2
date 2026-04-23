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
from src.api.ai_routes import router as ai_router
from src.db.transaction_db import init_db, get_transaction, update_transaction_status
from src.agents.arbitrator import Arbitrator
from src.anchor.anchor_service import AnchorService
from src.anchor.scheduler import AnchorScheduler
from src.db.transaction_db import TransactionDB as CoreDB
from src.crypto.tron_chain import TronChainService

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
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # Production frontend
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)
app.include_router(ai_router)

# Global instances
core_db: CoreDB = None
anchor_scheduler: AnchorScheduler = None
auto_confirm_service = None

class DisputeRequest(BaseModel):
    reason: Optional[str] = "Hash mismatch or non-delivery"

from src.utils.batch_writer import log_writer, referral_writer

@app.on_event("startup")
async def startup_event():
    global core_db, anchor_scheduler, auto_confirm_service
    
    # Initialize Core DB (1号员工)
    await init_db()
    core_db = CoreDB(os.getenv("DB_PATH", "./black2.db"))
    
    # Start async batch writers for high-concurrency optimization
    await log_writer.start()
    await referral_writer.start()
    
    # Initialize Anchor Service (2号员工)
    anchor_service = AnchorService(core_db)
    interval = int(os.getenv("ANCHOR_INTERVAL_HOURS", "1"))
    anchor_scheduler = AnchorScheduler(anchor_service, interval)
    anchor_scheduler.start()
    
    # Initialize Auto-Confirm Service
    from src.anchor.auto_confirm import auto_confirm_service as acs
    auto_confirm_service = acs
    await auto_confirm_service.initialize_pending_countdowns()
    
    # Initialize Arbitration Timer Service
    from src.anchor.arbitration_timer import arbitration_timer_service as ats
    await ats.initialize_pending_arbitrations()
    
    # Start Local Settlement Worker (for Windows compatibility)
    try:
        from src.utils.local_worker import start_listener
        start_listener()
    except Exception as e:
        print(f"Warning: Could not start local worker: {e}")
    
    print("Black2 System Started: API + Anchoring + Arbitration + AutoConfirm + Worker")

@app.on_event("shutdown")
async def shutdown_event():
    if anchor_scheduler:
        await anchor_scheduler.stop()
    # Stop batch writers gracefully
    await log_writer.stop()
    await referral_writer.stop()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
