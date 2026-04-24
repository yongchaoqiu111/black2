# Black2 SDK Structure Context

## 1. SDK Entry Point
**File:** `black2-sdk/black2/client.py`
```python
class B2PClient:
    def __init__(self, local_mode=False):
        self.engine = ReputationEngine()
        self.storage = StorageAdapter()
        # TODO: Integrate X402Bridge here

    def check_agent_risk(self, agent_id):
        """Check risk level before transaction"""
        pass

    def record_transaction(self, agent_id, success, amount):
        """Update reputation after transaction"""
        pass
```

## 2. Reputation Engine
**File:** `black2-sdk/black2/reputation.py`
```python
class ReputationEngine:
    def calculate_friction_coefficient(self, data):
        """
        Calculate friction based on score, win_rate, and dispute_count.
        Higher friction means higher staking requirement.
        """
        pass
```

## 3. Dependency Management
**File:** `black2-sdk/setup.py`
```python
install_requires=[
    "requests",
    "pygit2",
    # TODO: Add "uvd-x402-sdk"
]
```

## 4. Integration Goal
*   Provide a unified method like `client.pay_with_escrow()` that handles both reputation check and X402 payment locking.
