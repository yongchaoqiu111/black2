"""
Black2 Protocol Client

AI transaction trust layer unified entry point.
Integrates with X402 protocol for escrow payments and fund release.
"""

from .reputation import ReputationEngine
from .storage import StorageAdapter
from .models import ReputationData, RiskLevel
from .x402_bridge import X402Bridge
import json
import os

class B2PClient:
    """
    Black2 Protocol Client: Unified entry point for AI transaction trust layer.
    Integrates with X402 for secure escrow payments.
    """

    def __init__(self, github_token=None, ipfs_host="http://127.0.0.1:5001", local_mode=False,
                 x402_api_key=None, x402_network=None):
        self.engine = ReputationEngine()
        
        if local_mode:
            from pathlib import Path
            self.storage = type('LocalStorage', (), {
                'pull_reputation': lambda self, agent_id: self._load_local(agent_id),
                'push_reputation': lambda self, agent_id, data: self._save_local(agent_id, data)
            })()
            self.workspace = Path("./b2p_data")
            self.workspace.mkdir(exist_ok=True)
        else:
            self.storage = StorageAdapter(github_token=github_token, ipfs_host=ipfs_host)
        
        self.x402 = X402Bridge(api_key=x402_api_key, network=x402_network)

    def _load_local(self, agent_id):
        repo_path = self.workspace / f"{agent_id}.json"
        if not repo_path.exists():
            return None
        with open(repo_path, 'r') as f:
            data = json.load(f)
        return ReputationData(**data)

    def _save_local(self, agent_id, data):
        repo_path = self.workspace / f"{agent_id}.json"
        with open(repo_path, 'w') as f:
            json.dump(data.__dict__, f, indent=2, default=str)

    def check_agent_risk(self, agent_id, github_owner=None, github_repo=None):
        """
        Query risk level of specified AI Agent.
        """
        print(f"[B2P] Checking risk for {agent_id}...")
        
        if github_owner and github_repo:
            repo_data = self.storage.pull_repo_data(github_owner, github_repo)
        else:
            repo_data = self.storage.pull_reputation(agent_id)
        
        if not repo_data:
            return {"error": "Repo data not found or invalid", "risk_level": RiskLevel.CRITICAL}

        assessment = {
            "risk_level": self.engine.get_risk_level(repo_data),
            "friction_coefficient": self.engine.calculate_friction_coefficient(repo_data),
            "total_score": repo_data.total_score
        }
        return assessment

    def record_transaction(self, agent_id, success: bool, amount: float, 
                           was_disputed: bool = False, dispute_won: bool = False,
                           github_owner=None, github_repo=None):
        """
        Record a transaction result and update reputation repository.
        """
        print(f"[B2P] Recording transaction for {agent_id}...")
        
        if github_owner and github_repo:
            repo_data = self.storage.pull_repo_data(github_owner, github_repo)
        else:
            repo_data = self.storage.pull_reputation(agent_id)
        
        if not repo_data:
            repo_data = ReputationData(agent_id=agent_id)
        
        updated_data = self.engine.update_reputation(
            repo_data, success, amount, was_disputed, dispute_won
        )
        
        if github_owner and github_repo:
            self.storage.push_to_github(github_owner, github_repo, "b2p-repo.json", updated_data.__dict__)
        else:
            self.storage.push_reputation(agent_id, updated_data)
            
        return {"success": True, "new_score": updated_data.total_score}

    async def create_escrow_transaction(self, sender: str, receiver: str, amount: float, 
                                        asset: str = "USDC") -> dict:
        """
        Create an escrow transaction via X402 protocol.
        
        Args:
            sender: Sender's address
            receiver: Receiver's address
            amount: Transaction amount
            asset: Asset type (default: USDC)
            
        Returns:
            Dict with escrow details
        """
        print(f"[B2P] Creating escrow transaction: {amount} {asset} from {sender} to {receiver}")
        
        result = await self.x402.initiate_escrow_payment(
            sender=sender,
            receiver=receiver,
            amount=amount,
            asset=asset
        )
        
        return {
            "escrow_id": result.escrow_id,
            "escrow_address": result.escrow_address,
            "status": result.status,
            "amount": result.amount,
            "asset": result.asset
        }

    async def release_escrow(self, escrow_id: str, recipient: str, verdict: str) -> dict:
        """
        Release escrow based on arbitration verdict.
        
        Args:
            escrow_id: ID of the escrow
            recipient: Address to receive funds
            verdict: 'seller_wins' or 'buyer_wins'
            
        Returns:
            Dict with release details
        """
        print(f"[B2P] Releasing escrow {escrow_id} to {recipient}, verdict: {verdict}")
        
        result = await self.x402.release_funds(
            escrow_id=escrow_id,
            recipient=recipient,
            verdict=verdict
        )
        
        return {
            "success": result.success,
            "tx_hash": result.tx_hash,
            "recipient": result.recipient,
            "verdict": result.verdict,
            "message": result.message
        }

    async def get_escrow_balance(self, agent_id: str, asset: str = "USDC") -> dict:
        """
        Get X402 escrow balance for an agent.
        
        Args:
            agent_id: Agent's address
            asset: Asset type (default: USDC)
            
        Returns:
            Dict with balance information
        """
        print(f"[B2P] Getting X402 balance for {agent_id}")
        
        balance = await self.x402.check_balance(agent_id=agent_id, asset=asset)
        return balance

    def is_x402_available(self) -> bool:
        """Check if X402 integration is available"""
        return self.x402.is_available()
