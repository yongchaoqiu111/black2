"""
Black2 Clearing Protocol - Main Server

Provides API endpoints for anchoring transaction root hashes.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .anchor import AnchorService, AnchorScheduler
from .db import TransactionDB

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ANCHOR_INTERVAL_HOURS = int(os.getenv("ANCHOR_INTERVAL_HOURS", "1"))
DB_PATH = os.getenv("DB_PATH", "./backend/data/clearing.db")

db: TransactionDB = None
anchor_service: AnchorService = None
scheduler: AnchorScheduler = None


class AnchorTriggerResponse(BaseModel):
    success: bool
    message: str
    data: dict = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, anchor_service, scheduler

    db = TransactionDB(DB_PATH)
    await db.initialize()

    anchor_service = AnchorService(db)
    scheduler = AnchorScheduler(anchor_service, ANCHOR_INTERVAL_HOURS)
    scheduler.start()

    logger.info("Black2 Anchor Service started")

    yield

    await scheduler.stop()
    await db.close()
    logger.info("Black2 Anchor Service stopped")


app = FastAPI(
    title="Black2 Anchor Service",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/api/v1/anchor/trigger", response_model=AnchorTriggerResponse)
async def trigger_anchor():
    result = await scheduler.trigger_now()

    if "message" in result and result["message"] == "No unanchored transactions":
        return AnchorTriggerResponse(
            success=True,
            message="No unanchored transactions found"
        )

    return AnchorTriggerResponse(
        success=True,
        message="Anchor completed successfully",
        data=result
    )


@app.get("/api/v1/anchor/status")
async def get_anchor_status():
    latest_anchor = await db.get_latest_anchor()
    all_txs = await db.get_all_transactions()
    unanchored_count = sum(1 for tx in all_txs if tx["anchor_hash"] is None)

    return {
        "latest_anchor": latest_anchor,
        "total_transactions": len(all_txs),
        "unanchored_transactions": unanchored_count,
        "scheduler_running": scheduler._running if scheduler else False
    }


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)