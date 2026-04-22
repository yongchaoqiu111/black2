from typing import Dict, Optional
from datetime import datetime
from models import WalletProfile, PointsAccount
from config import Config

class ReputationSystem:
    def __init__(self):
        self.profiles: Dict[str, WalletProfile] = {}
        self.points: Dict[str, PointsAccount] = {}

    def get_profile(self, wallet_id: str) -> WalletProfile:
        if wallet_id not in self.profiles:
            self.profiles[wallet_id] = WalletProfile(wallet_id=wallet_id)
        return self.profiles[wallet_id]

    def get_points(self, wallet_id: str) -> PointsAccount:
        if wallet_id not in self.points:
            self.points[wallet_id] = PointsAccount(wallet_id=wallet_id)
        return self.points[wallet_id]

    def calculate_reputation_score(self, profile: WalletProfile) -> int:
        buy_rate = profile.success_buys / max(profile.total_buys, 1)
        total_ratings = profile.positive_count + profile.neutral_count + profile.negative_count
        positive_rate = profile.positive_count / max(total_ratings, 1)
        no_violation = 1.0 if profile.violation_count == 0 else 0.5

        score = (
            buy_rate * Config.REPUTATION_WEIGHTS["buy_success_rate"] +
            positive_rate * Config.REPUTATION_WEIGHTS["positive_rate"] +
            no_violation * Config.REPUTATION_WEIGHTS["no_violation"]
        ) * 100

        if profile.is_frozen:
            score = min(score, 20)

        return int(min(max(score, 0), 100))

    def update_profile(self, wallet_id: str, **kwargs):
        profile = self.get_profile(wallet_id)
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.now()
        profile.score = self.calculate_reputation_score(profile)

        if profile.score >= 80:
            profile.level = "high"
        elif profile.score >= 60:
            profile.level = "medium"
        elif profile.score >= 40:
            profile.level = "low"
        else:
            profile.level = "critical"

        return profile

    def add_reward_points(self, wallet_id: str, source: str, amount: int = None):
        points = self.get_points(wallet_id)
        multiplier = Config.POINTS_CONFIG["founder_multiplier"] if wallet_id == Config.FOUNDER_WALLET else 1

        if amount is None:
            if source == "event":
                amount = Config.POINTS_CONFIG["event_reward"]
            elif source == "rating":
                amount = Config.POINTS_CONFIG["rating_reward"]
            else:
                amount = Config.POINTS_CONFIG["base_reward"]

        reward = amount * multiplier
        points.balance += reward
        points.total_earned += reward
        points.updated_at = datetime.now()
        return reward

    def consume_points(self, wallet_id: str, amount: int) -> bool:
        points = self.get_points(wallet_id)
        if points.balance >= amount:
            points.balance -= amount
            points.total_burned += amount
            points.updated_at = datetime.now()
            return True
        return False

    def process_transaction(self, tx_id: str, buyer: str, seller: str, amount: float):
        buyer_profile = self.get_profile(buyer)
        buyer_profile.total_buys += 1
        seller_profile = self.get_profile(seller)
        seller_profile.total_sells += 1

        self.add_reward_points(buyer, "event")
        self.add_reward_points(seller, "event")

        self.update_profile(buyer)
        self.update_profile(seller)

    def process_rating(self, wallet_id: str, target_wallet: str, rating: str):
        target_profile = self.get_profile(target_wallet)

        if rating == "positive":
            target_profile.positive_count += 1
        elif rating == "neutral":
            target_profile.neutral_count += 1
        elif rating == "negative":
            target_profile.negative_count += 1

        self.add_reward_points(wallet_id, "rating")
        self.update_profile(target_wallet)

    def check_trade_allowed(self, wallet_id: str) -> Dict:
        profile = self.get_profile(wallet_id)
        return {
            "allowed": not profile.is_frozen and profile.score >= 40,
            "level": profile.level,
            "score": profile.score,
            "daily_buy_limit": None if profile.level in ["high", "medium"] else 10,
            "daily_sell_limit": None if profile.level in ["high", "medium"] else 20,
        }


reputation = ReputationSystem()