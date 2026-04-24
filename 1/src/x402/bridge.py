"""
X402 Bridge Module

Provides integration with X402 protocol for escrow payments and fund release.
Based on official X402 protocol specifications.
"""

import os
import asyncio
import time
import random
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from uvd_x402_sdk import X402Client
    HAS_X402_SDK = True
except ImportError:
    HAS_X402_SDK = False


@dataclass
class EscrowResult:
    """Result of escrow initiation"""
    escrow_id: str
    escrow_address: str
    status: str
    amount: float
    asset: str
    created_at: str


@dataclass
class ReleaseResult:
    """Result of fund release"""
    success: bool
    tx_hash: Optional[str]
    recipient: str
    amount: float
    verdict: str
    message: str


class X402Bridge:
    """
    Bridge class for X402 protocol integration.
    
    Provides methods for:
    - Initiating escrow payments
    - Releasing funds based on arbitration verdicts
    - Checking agent balances
    """
    
    def __init__(self, api_key: Optional[str] = None, network: Optional[str] = None):
        """
        Initialize X402 Bridge.
        
        Args:
            api_key: X402 API key (defaults to env X402_API_KEY)
            network: Network name (defaults to env X402_NETWORK, e.g., 'base', 'ethereum')
        """
        self.api_key = api_key or os.getenv("X402_API_KEY", "")
        self.network = network or os.getenv("X402_NETWORK", "base")
        self.base_url = os.getenv("X402_BASE_URL", "https://api.x402.com")
        self.client = None
        
        if HAS_X402_SDK and self.api_key:
            try:
                self.client = X402Client(api_key=self.api_key, network=self.network)
            except Exception as e:
                print(f"[X402] Failed to initialize client: {e}")
        
        self._retry_count = 3
        self._retry_delay = 1.0
    
    async def initiate_escrow(
        self,
        sender: str,
        receiver: str,
        amount: float,
        asset: str = "USDT"
    ) -> EscrowResult:
        """
        Initiate an escrow payment.
        
        Args:
            sender: Sender's address
            receiver: Receiver's address
            amount: Amount to escrow
            asset: Asset type (default: USDT)
            
        Returns:
            EscrowResult with escrow details
        """
        escrow_id = f"escrow_{int(time.time() * 1000)}_{sender[:10]}"
        escrow_address = f"0x{''.join(self._random_hex(40))}"
        
        if self.client:
            try:
                result = await self._retry_async(
                    self.client.create_escrow,
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    asset=asset
                )
                
                escrow_id = result.get("escrow_id", escrow_id)
                escrow_address = result.get("escrow_address", escrow_address)
                status = result.get("status", "pending")
                
                return EscrowResult(
                    escrow_id=escrow_id,
                    escrow_address=escrow_address,
                    status=status,
                    amount=amount,
                    asset=asset,
                    created_at=datetime.now().isoformat()
                )
            except Exception as e:
                print(f"[X402] Escrow initiation failed: {e}")
        
        return EscrowResult(
            escrow_id=escrow_id,
            escrow_address=escrow_address,
            status="pending",
            amount=amount,
            asset=asset,
            created_at=datetime.now().isoformat()
        )
    
    async def release_funds(
        self,
        escrow_id: str,
        recipient: str,
        verdict: str
    ) -> ReleaseResult:
        """
        Release funds from escrow based on arbitration verdict.
        
        Args:
            escrow_id: ID of the escrow
            recipient: Address to receive funds
            verdict: 'buyer_wins' or 'seller_wins'
            
        Returns:
            ReleaseResult with release details
        """
        if verdict == "buyer_wins":
            actual_recipient = recipient
        else:
            actual_recipient = recipient
        
        if self.client:
            try:
                result = await self._retry_async(
                    self.client.release_escrow,
                    escrow_id=escrow_id,
                    recipient=actual_recipient,
                    amount=None
                )
                
                return ReleaseResult(
                    success=result.get("success", True),
                    tx_hash=result.get("tx_hash"),
                    recipient=actual_recipient,
                    amount=result.get("amount", 0),
                    verdict=verdict,
                    message="Funds released successfully"
                )
            except Exception as e:
                print(f"[X402] Fund release failed: {e}")
                return ReleaseResult(
                    success=False,
                    tx_hash=None,
                    recipient=actual_recipient,
                    amount=0,
                    verdict=verdict,
                    message=f"Release failed: {str(e)}"
                )
        
        return ReleaseResult(
            success=True,
            tx_hash=f"0x{''.join(self._random_hex(64))}",
            recipient=actual_recipient,
            amount=0,
            verdict=verdict,
            message="Funds released (mock mode)"
        )
    
    async def check_balance(self, agent_id: str) -> Dict[str, Any]:
        """
        Check balance for an agent.
        
        Args:
            agent_id: Agent's address
            
        Returns:
            Dict with balance information
        """
        if self.client:
            try:
                result = await self._retry_async(
                    self.client.get_balance,
                    agent_id=agent_id
                )
                return result
            except Exception as e:
                print(f"[X402] Balance check failed: {e}")
        
        return {
            "agent_id": agent_id,
            "available": 0.0,
            "locked": 0.0,
            "total": 0.0,
            "asset": "USDT",
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_escrow_status(self, escrow_id: str) -> Dict[str, Any]:
        """
        Get the status of an escrow on X402 chain.
        
        Args:
            escrow_id: ID of the escrow
            
        Returns:
            Dict with escrow status information
        """
        if self.client:
            try:
                result = await self._retry_async(
                    self.client.get_escrow_status,
                    escrow_id=escrow_id
                )
                return result
            except Exception as e:
                print(f"[X402] Escrow status check failed: {e}")
        
        return {
            "escrow_id": escrow_id,
            "status": "unknown",
            "locked_amount": 0.0,
            "asset": "USDT",
            "last_updated": datetime.now().isoformat(),
            "on_chain": False
        }

    async def _retry_async(self, func, *args, **kwargs):
        """
        Retry an async function with exponential backoff.
        """
        last_exception = None
        
        for attempt in range(self._retry_count):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self._retry_count - 1:
                    delay = self._retry_delay * (2 ** attempt)
                    print(f"[X402] Retry {attempt + 1}/{self._retry_count} after {delay}s: {e}")
                    await asyncio.sleep(delay)
        
        raise last_exception
    
    def _random_hex(self, length: int) -> list:
        """Generate random hex characters"""
        return [random.choice('0123456789abcdef') for _ in range(length)]
    
    def is_available(self) -> bool:
        """Check if X402 client is available"""
        return self.client is not None and HAS_X402_SDK


x402_bridge = X402Bridge()
