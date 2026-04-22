from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class WalletProfile(BaseModel):
    wallet_id: str
    score: int = 60
    level: str = "medium"
    total_buys: int = 0
    success_buys: int = 0
    total_sells: int = 0
    success_sells: int = 0
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    violation_count: int = 0
    is_frozen: bool = False
    updated_at: datetime = datetime.now()

class Transaction(BaseModel):
    tx_id: str
    buyer_wallet: str
    seller_wallet: str
    amount: float
    status: str = "pending"
    rating: Optional[str] = None
    created_at: datetime = datetime.now()

class PointsAccount(BaseModel):
    wallet_id: str
    balance: int = 0
    total_earned: int = 0
    total_burned: int = 0
    updated_at: datetime = datetime.now()