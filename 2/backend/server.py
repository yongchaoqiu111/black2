"""
Black2 X402 Integration Server

Main entry point for the Black2 clearing API with X402 on-chain anchoring.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Import modules
from src.anchor import (
    GitHubAnchorService,
    github_anchor,
    X402OnChainAnchor,
    x402_anchor,
    DualAnchorService,
    arbitration_timer_service
)
from src.db import TransactionDB
from src.utils import task_processor
from src.x402 import x402_bridge

load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
db: Optional[TransactionDB] = None
dual_anchor: Optional[DualAnchorService] = None

# Pydantic models
class ArbitrationRequest(BaseModel):
    arbitration_id: str
    verdict: str
    commit_hash: str
    metadata: Optional[Dict[str, Any]] = None

class VerdictExecutionRequest(BaseModel):
    tx_id: str
    verdict: str

class CountdownRequest(BaseModel):
    tx_id: str
    hours: int = 48

class BatchAnchorRequest(BaseModel):
    batch_id: Optional[str] = None
    transaction_hashes: Optional[List[str]] = None
    limit: Optional[int] = 100

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    stats: Optional[Dict[str, Any]] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, dual_anchor
    
    # Initialize Database
    db_path = os.getenv("DB_PATH", "./backend/data/clearing.db")
    db = TransactionDB(db_path)
    await db.initialize()
    logger.info("Database initialized")
    
    # Initialize Dual Anchor Service
    dual_anchor = DualAnchorService(github_anchor, x402_anchor)
    logger.info("Dual Anchor Service initialized")
    
    # Start Async Task Processor
    await task_processor.start()
    logger.info("Async Task Processor started")
    
    # Initialize Arbitration Timer Service
    arbitration_timer_service.initialize(
        db_path=db_path,
        task_processor=task_processor,
        x402_bridge=x402_bridge,
        github_anchor=github_anchor,
        x402_anchor=x402_anchor
    )
    logger.info("Arbitration Timer Service initialized")
    
    # Initialize pending arbitrations
    await arbitration_timer_service.initialize_pending_arbitrations()
    
    print("\n" + "="*60)
    print("Black2 X402 Integration Service Started")
    print("="*60)
    print(f"X402 Enabled: {x402_anchor.enabled}")
    print(f"X402 Chain ID: {x402_anchor.chain_id}")
    print(f"GitHub Repo: {github_anchor.owner}/{github_anchor.repo}")
    print("="*60 + "\n")
    
    yield
    
    # Cleanup
    await task_processor.stop()
    await db.close()
    logger.info("Black2 X402 Integration Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Black2 X402 Integration Service",
    description="Black2 协议锚点服务，支持 GitHub 和 X402 双重链上存证，以及异步仲裁处理",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routes
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    services_status = {
        "database": "healthy" if db else "disconnected",
        "github_anchor": "healthy" if github_anchor else "disconnected",
        "x402_anchor": "enabled" if x402_anchor.enabled else "disabled",
        "async_processor": "running" if task_processor.running else "stopped",
        "arbitration_timer": "initialized" if arbitration_timer_service.db_path else "not_initialized"
    }
    
    stats = None
    if db:
        stats = await db.get_anchor_stats()
    
    return HealthResponse(
        status="healthy",
        services=services_status,
        stats=stats
    )


@app.get("/api/v1/anchor/status")
async def get_anchor_status():
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    latest_anchor = await db.get_latest_anchor()
    stats = await db.get_anchor_stats()
    processor_stats = task_processor.get_stats()
    
    return {
        "latest_anchor": latest_anchor,
        "stats": stats,
        "processor": processor_stats,
        "x402_enabled": x402_anchor.enabled,
        "x402_chain_id": x402_anchor.chain_id
    }


@app.post("/api/v1/anchor/arbitration")
async def anchor_arbitration(request: ArbitrationRequest):
    if not dual_anchor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dual Anchor Service not available"
        )
    
    # First, store arbitration in DB
    await db.add_arbitration(
        arbitration_id=request.arbitration_id,
        verdict=request.verdict,
        metadata=request.metadata,
        github_commit_hash=request.commit_hash,
        x402_tx_hash=None
    )
    
    # Submit anchor to background task to avoid blocking
    async def anchor_task():
        try:
            result = await dual_anchor.anchor_arbitration_result(
                arbitration_id=request.arbitration_id,
                verdict=request.verdict,
                commit_hash=request.commit_hash,
                metadata=request.metadata
            )
            
            if db:
                await db.add_anchor_record(
                    anchor_type="arbitration",
                    root_hash=None,
                    transaction_count=None,
                    github_commit_hash=request.commit_hash,
                    github_commit_url=None,
                    x402_tx_hash=result.get("x402_tx_hash"),
                    x402_chain_id=x402_anchor.chain_id if x402_anchor.enabled else None,
                    anchor_timestamp=datetime.now(timezone.utc).isoformat(),
                    success=result.get("x402_success", False),
                    error_message=result.get("x402_error")
                )
                
                if result.get("x402_success"):
                    await db._db.execute(
                        """UPDATE arbitrations
                           SET x402_tx_hash = ?
                           WHERE arbitration_id = ?""",
                        (result.get("x402_tx_hash"), request.arbitration_id)
                    )
                    await db._db.commit()
            
            logger.info(f"Arbitration anchor completed for {request.arbitration_id}")
            return result
        except Exception as e:
            logger.error(f"Arbitration anchor failed for {request.arbitration_id}: {e}", exc_info=True)
            raise
    
    await task_processor.submit_task(anchor_task)
    
    return {
        "success": True,
        "message": "Arbitration anchor submitted to background processing",
        "arbitration_id": request.arbitration_id
    }


@app.post("/api/v1/anchor/batch")
async def anchor_batch(request: BatchAnchorRequest):
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    transaction_hashes = request.transaction_hashes
    
    if not transaction_hashes:
        unanchored = await db.get_unanchored_transactions(request.limit)
        transaction_hashes = [tx["tx_hash"] for tx in unanchored]
    
    if not transaction_hashes:
        return {
            "success": True,
            "message": "No transactions to anchor",
            "transaction_count": 0
        }
    
    batch_id = request.batch_id or f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    
    # Submit to background task
    async def batch_anchor_task():
        try:
            github_result = await github_anchor.anchor_transaction_batch(
                transaction_hashes=transaction_hashes,
                batch_id=batch_id
            )
            
            result = await dual_anchor.anchor_batch_with_x402(
                transaction_hashes=transaction_hashes,
                batch_id=batch_id,
                github_result=github_result
            )
            
            if db:
                anchor_timestamp = datetime.now(timezone.utc).isoformat()
                await db.anchor_transactions(
                    tx_hashes=transaction_hashes,
                    anchor_hash=result.get("merkle_root"),
                    anchor_timestamp=anchor_timestamp,
                    x402_tx_hash=result.get("x402_batch_tx_hash")
                )
                
                await db.add_anchor_record(
                    anchor_type="transaction_batch",
                    root_hash=result.get("merkle_root"),
                    transaction_count=len(transaction_hashes),
                    github_commit_hash=result.get("github_commit_hash"),
                    github_commit_url=result.get("github_commit_url"),
                    x402_tx_hash=result.get("x402_batch_tx_hash"),
                    x402_chain_id=x402_anchor.chain_id if x402_anchor.enabled else None,
                    anchor_timestamp=anchor_timestamp,
                    success=result.get("x402_success", False)
                )
            
            logger.info(f"Batch anchor completed: {batch_id}, tx count: {len(transaction_hashes)}")
            return result
        except Exception as e:
            logger.error(f"Batch anchor failed for {batch_id}: {e}", exc_info=True)
            raise
    
    await task_processor.submit_task(batch_anchor_task)
    
    return {
        "success": True,
        "message": "Batch anchor submitted to background processing",
        "batch_id": batch_id,
        "transaction_count": len(transaction_hashes)
    }


@app.get("/api/v1/transactions")
async def get_transactions(limit: Optional[int] = 50):
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    transactions = await db.get_all_transactions(limit)
    return {
        "transactions": transactions,
        "count": len(transactions)
    }


@app.post("/api/v1/retry-pending")
async def retry_pending_anchors():
    if not dual_anchor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dual Anchor Service not available"
        )
    
    await dual_anchor.retry_pending_chain_anchors()
    
    pending_count = await dual_anchor.get_pending_count()
    
    return {
        "success": True,
        "message": "Retry triggered",
        "pending_count": pending_count
    }


@app.post("/api/v1/x402/switch-chain")
async def switch_chain(chain_name: str):
    success = await x402_anchor.switch_chain(chain_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chain {chain_name} not supported. Supported chains: {list(x402_anchor.SUPPORTED_CHAINS.keys())}"
        )
    
    return {
        "success": True,
        "message": f"Switched to {chain_name} chain",
        "chain_id": x402_anchor.chain_id
    }


@app.get("/api/v1/x402/supported-chains")
async def get_supported_chains():
    return {
        "supported_chains": x402_anchor.SUPPORTED_CHAINS,
        "current_chain_id": x402_anchor.chain_id
    }


# ==========================================
# Arbitration Engine API Routes
# ==========================================

@app.post("/api/v1/arbitration/start-countdown")
async def start_arbitration_countdown(request: CountdownRequest):
    if not arbitration_timer_service.db_path:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Arbitration timer service not initialized"
        )
    
    await arbitration_timer_service.start_arbitration_countdown(
        tx_id=request.tx_id,
        hours=request.hours
    )
    
    return {
        "success": True,
        "message": "Arbitration countdown started",
        "tx_id": request.tx_id,
        "hours": request.hours
    }


@app.get("/api/v1/arbitration/countdown-status/{tx_id}")
async def get_countdown_status(tx_id: str):
    status = arbitration_timer_service.get_countdown_status(tx_id)
    
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No countdown found for tx {tx_id}"
        )
    
    return status


@app.post("/api/v1/arbitration/cancel-countdown/{tx_id}")
async def cancel_countdown(tx_id: str):
    if not arbitration_timer_service.db_path:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Arbitration timer service not initialized"
        )
    
    await arbitration_timer_service.cancel_countdown(tx_id)
    
    return {
        "success": True,
        "message": "Countdown cancelled",
        "tx_id": tx_id
    }


@app.post("/api/v1/arbitration/execute-verdict")
async def execute_arbitration_verdict(request: VerdictExecutionRequest):
    if not arbitration_timer_service.db_path:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Arbitration timer service not initialized"
        )
    
    if request.verdict not in ["seller_wins", "buyer_wins"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verdict must be either 'seller_wins' or 'buyer_wins'"
        )
    
    # Execute verdict (this submits to background task)
    await arbitration_timer_service.execute_arbitration_verdict(
        tx_id=request.tx_id,
        verdict=request.verdict
    )
    
    return {
        "success": True,
        "message": "Verdict execution submitted to background processing",
        "tx_id": request.tx_id,
        "verdict": request.verdict
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
