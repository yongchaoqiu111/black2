import os

class Config:
    FOUNDER_WALLET = "0x1234567890abcdef1234567890abcdef12345678"
    
    CURRENT_ALGO_VERSION = 1
    
    TOTAL_SHARDS = 5
    
    REPLICA_COUNT = 3
    
    POINTS_CONFIG = {
        "founder_multiplier": 1000,
        "base_reward": 1,
        "event_reward": 10,
        "rating_reward": 5,
    }
    
    REPUTATION_WEIGHTS = {
        "buy_success_rate": 0.30,
        "pay_success_rate": 0.20,
        "positive_rate": 0.40,
        "no_violation": 0.10,
    }
    
    STORAGE_NODES = [
        {"name": "ipfs", "url": "https://ipfs.io/api/v0/add"},
        {"name": "github", "url": "https://api.github.com/repos/your/repo/contents"},
        {"name": "local", "path": "./shards/"},
    ]