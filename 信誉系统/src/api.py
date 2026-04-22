from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from reputation import reputation
from shard import get_algorithm
from storage import storage
import uuid

app = FastAPI(title="AI信誉系统", version="1.0")

class EventRequest(BaseModel):
    event_type: str
    buyer_wallet: str
    seller_wallet: str
    tx_id: Optional[str] = None
    rating: Optional[str] = None
    amount: float = 0

class BatchCheckRequest(BaseModel):
    wallets: List[str]


@app.get("/v1/check/{wallet_id}")
async def check_wallet(wallet_id: str, x_wallet_id: str = Header(None)):
    result = reputation.check_trade_allowed(wallet_id)
    return result


@app.post("/v1/batch/check")
async def batch_check(request: BatchCheckRequest, x_wallet_id: str = Header(None)):
    results = {}
    for wallet_id in request.wallets[:50]:
        results[wallet_id] = reputation.check_trade_allowed(wallet_id)

    billing = {}
    if len(request.wallets) > 50:
        billing = {"billable_count": len(request.wallets) - 50, "cost": 0.008}

    return {"results": results, "billing": billing}


@app.get("/v1/profile/{wallet_id}")
async def get_profile(wallet_id: str):
    profile = reputation.get_profile(wallet_id)
    points = reputation.get_points(wallet_id)

    return {
        "score": profile.score,
        "level": profile.level,
        "buy_success_rate": profile.success_buys / max(profile.total_buys, 1),
        "sell_success_rate": profile.success_sells / max(profile.total_sells, 1),
        "positive_rate": profile.positive_count / max(profile.positive_count + profile.neutral_count + profile.negative_count, 1),
        "recent_violation": profile.violation_count > 0,
        "points_balance": points.balance,
    }


@app.get("/v1/full/{wallet_id}")
async def get_full_profile(wallet_id: str, x_wallet_id: str = Header(None)):
    if not reputation.consume_points(x_wallet_id, 20):
        raise HTTPException(status_code=402, detail="Insufficient points")

    profile = reputation.get_profile(wallet_id)
    points = reputation.get_points(wallet_id)

    return {
        "profile": profile.dict(),
        "points": points.dict(),
    }


@app.post("/v1/event")
async def handle_event(request: EventRequest, x_wallet_id: str = Header(None)):
    if request.event_type == "transaction_completed":
        reputation.process_transaction(
            request.tx_id or str(uuid.uuid4()),
            request.buyer_wallet,
            request.seller_wallet,
            request.amount
        )

        points = reputation.get_points(x_wallet_id)

        return {
            "status": "accepted",
            "points": {
                "earned": 10,
                "balance": points.balance
            }
        }

    elif request.event_type == "rating":
        reputation.process_rating(x_wallet_id, request.seller_wallet, request.rating)

        points = reputation.get_points(x_wallet_id)

        return {
            "status": "accepted",
            "points": {
                "earned": 5,
                "balance": points.balance
            }
        }

    return {"status": "rejected", "reason": "unknown event_type"}


@app.get("/v1/points/balance")
async def get_points_balance(x_wallet_id: str = Header(None)):
    points = reputation.get_points(x_wallet_id)
    return {
        "balance": points.balance,
        "total_earned": points.total_earned,
        "total_burned": points.total_burned,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)