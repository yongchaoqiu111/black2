"""
Black2 Python SDK

A lightweight, async-first SDK for interacting with the Black2 AI-to-AI trading infrastructure.
"""

import httpx
from typing import Optional, Dict, Any
from .exceptions import Black2APIError


class Black2Client:
    """Main client for Black2 protocol interaction"""
    
    def __init__(self, api_base: str = "http://localhost:3000/api/v1", api_key: Optional[str] = None):
        """
        Initialize Black2 client
        
        Args:
            api_base: Black2 API base URL
            api_key: Optional API key for authentication (if required in future)
        """
        self.api_base = api_base.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            headers={"Content-Type": "application/json"}
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Internal request handler with standardized error parsing"""
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            data = response.json()
            
            # Handle standardized response format {code, message, data}
            if "code" in data:
                if data["code"] >= 4000:
                    raise Black2APIError(
                        code=data["code"],
                        message=data.get("message", "Unknown error"),
                        detail=data.get("data")
                    )
                return data
            
            # Fallback for non-standard responses
            if response.status_code >= 400:
                raise Black2APIError(
                    code=response.status_code,
                    message=data.get("detail", "Request failed"),
                    detail=data
                )
            
            return {"code": 200, "message": "Success", "data": data}
            
        except httpx.HTTPError as e:
            raise Black2APIError(code=5000, message=f"HTTP error: {str(e)}")
    
    # --- Transaction Management ---
    
    async def create_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        contract_hash: str,
        currency: str = "USDT"
    ) -> Dict[str, Any]:
        """
        Create a new transaction (escrow)
        
        Args:
            from_address: Buyer's wallet address
            to_address: Seller's wallet address
            amount: Transaction amount
            contract_hash: SHA-256 hash of the contract
            currency: Currency type (default: USDT)
            
        Returns:
            Transaction details including tx_id
        """
        payload = {
            "from_address": from_address,
            "to_address": to_address,
            "amount": amount,
            "currency": currency,
            "contract_hash": contract_hash
        }
        return await self._request("POST", "/transactions", json=payload)
    
    async def complete_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Complete a transaction and trigger fund release
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Completion status and fund release result
        """
        return await self._request("POST", f"/transactions/{tx_id}/complete")
    
    async def get_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Get transaction details
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Full transaction details
        """
        return await self._request("GET", f"/transactions/{tx_id}")
    
    # --- Reputation System ---
    
    async def get_reputation(self, address: str) -> Dict[str, Any]:
        """
        Get AI agent reputation score
        
        Args:
            address: Wallet address
            
        Returns:
            Reputation data including score and dispute history
        """
        return await self._request("GET", f"/reputation/{address}")
    
    # --- Arbitration Fund Pool ---
    
    async def get_arbitration_fund_pool(self) -> Dict[str, Any]:
        """
        Get arbitration fund pool statistics
        
        Returns:
            Fund pool balance and recent injections
        """
        return await self._request("GET", "/arbitration/fund-pool")
    
    # --- Dispute Management ---
    
    async def create_dispute(self, tx_id: str, reason: str) -> Dict[str, Any]:
        """
        Initiate a dispute for a transaction
        
        Args:
            tx_id: Transaction ID
            reason: Reason for dispute
            
        Returns:
            Dispute creation result
        """
        payload = {"reason": reason}
        return await self._request("POST", f"/transactions/{tx_id}/dispute", json=payload)


class TransactionManager:
    """Helper for batch transaction operations"""
    
    def __init__(self, client: Black2Client):
        self.client = client
    
    async def batch_create(self, transactions: list) -> list:
        """Create multiple transactions in parallel"""
        tasks = [
            self.client.create_transaction(**tx)
            for tx in transactions
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


class ReputationOracle:
    """Reputation data query and analysis"""
    
    def __init__(self, client: Black2Client):
        self.client = client
    
    async def check_risk_level(self, address: str) -> str:
        """
        Check risk level for an AI agent
        
        Returns: 'low', 'medium', 'high', 'critical'
        """
        rep = await self.client.get_reputation(address)
        score = rep.get('data', {}).get('reputation_score', 0)
        
        if score >= 80: return 'low'
        elif score >= 50: return 'medium'
        elif score >= 20: return 'high'
        else: return 'critical'
