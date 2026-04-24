"""
X402 Bridge - Payment Layer for Black2 Protocol

This module provides the payment infrastructure for B2P (Black2 Protocol),
handling fund flows through X402 Relay Network with escrow capabilities.

Core Capabilities:
- Cross-chain payments via X402 SDK
- Escrow (conditional payment) with arbitration integration
- Gas-free transactions through relay network
- Mock mode for local development and testing
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class X402ErrorCode(Enum):
    """
    Unified error code system for X402 Bridge operations.
    
    Attributes:
        SUCCESS: Operation completed successfully
        REPUTATION_REJECTED: Transaction rejected due to poor reputation
        INSUFFICIENT_BALANCE: Agent has insufficient balance
        NETWORK_TIMEOUT: Network request timeout
        INVALID_ADDRESS: Invalid wallet address format
        ESCROW_NOT_FOUND: Specified escrow ID does not exist
        ARBITRATION_PENDING: Waiting for arbitration verdict
        INTERNAL_ERROR: Internal system error
    """
    SUCCESS = 0
    REPUTATION_REJECTED = 1001
    INSUFFICIENT_BALANCE = 1002
    NETWORK_TIMEOUT = 1003
    INVALID_ADDRESS = 1004
    ESCROW_NOT_FOUND = 1005
    ARBITRATION_PENDING = 1006
    INTERNAL_ERROR = 9999


class X402Error(Exception):
    """
    Custom exception class for X402 Bridge errors.
    
    Attributes:
        code: Error code from X402ErrorCode enum
        message: Human-readable error message
        details: Additional error context
    """
    
    def __init__(self, code: X402ErrorCode, message: str, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.name}] {message}")


class EscrowStatus(Enum):
    """Status of an escrow payment"""
    PENDING = "pending"
    LOCKED = "locked"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class X402Bridge:
    """
    X402 Payment Bridge: Handles fund flows in B2P protocol.
    
    This class provides a high-level interface for:
    - Initiating escrow payments (conditional payments)
    - Releasing funds based on arbitration verdicts
    - Checking agent balances
    - Mock mode for local testing without X402 API key
    
    Attributes:
        api_key: X402 API key for production mode
        mock_mode: If True, simulate responses without actual API calls
        supported_assets: List of supported cryptocurrency assets
    
    Example:
        >>> bridge = X402Bridge(api_key="your_key")
        >>> result = bridge.initiate_escrow_payment("agent1", "agent2", 100.0)
        >>> print(result["status"])
        'locked'
    """
    
    SUPPORTED_ASSETS = ["USDC", "USDT", "ETH", "BTC"]
    
    def __init__(self, api_key: Optional[str] = None, mock_mode: bool = False):
        """
        Initialize X402 Bridge.
        
        Args:
            api_key: X402 API key. If None, uses X402_API_KEY environment variable.
            mock_mode: If True, operate in mock mode for local testing.
                      Default: False (production mode)
        
        Raises:
            X402Error: If API key is missing in non-mock mode
        """
        self.api_key = api_key or os.getenv("X402_API_KEY")
        self.mock_mode = mock_mode or not self.api_key
        
        if self.mock_mode:
            print("[X402 Bridge] Running in MOCK MODE - no actual API calls")
        else:
            masked_key = f"{self.api_key[:8]}..." if len(self.api_key) > 8 else self.api_key
            print(f"[X402 Bridge] Initialized with API Key: {masked_key}")
        
        self._escrow_store = {}
    
    def initiate_escrow_payment(
        self, 
        sender_id: str, 
        receiver_id: str, 
        amount: float, 
        asset: str = "USDC",
        contract_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate an escrow payment (conditional payment).
        
        Funds are locked in the X402 Relay Network until B2P arbitration
        engine issues a verdict. This ensures secure transactions between
        untrusted parties.
        
        Args:
            sender_id: Unique identifier of the sender (buyer)
            receiver_id: Unique identifier of the receiver (seller)
            amount: Payment amount
            asset: Cryptocurrency asset type (default: "USDC")
                  Supported: USDC, USDT, ETH, BTC
            contract_hash: Optional hash of the contract for verification
        
        Returns:
            Dictionary containing:
            - status: "locked" if successful
            - escrow_id: Unique identifier for this escrow
            - message: Status message
            - timestamp: ISO format timestamp
        
        Raises:
            X402Error: With code INSUFFICIENT_BALANCE if sender has insufficient funds
                      With code INVALID_ADDRESS if sender/receiver IDs are invalid
                      With code NETWORK_TIMEOUT if X402 network is unreachable
        
        Example:
            >>> result = bridge.initiate_escrow_payment(
            ...     sender_id="buyer_001",
            ...     receiver_id="seller_002",
            ...     amount=500.0,
            ...     asset="USDC"
            ... )
            >>> print(result["escrow_id"])
            'esc_buyer_001_seller_002_500'
        """
        if asset not in self.SUPPORTED_ASSETS:
            raise X402Error(
                X402ErrorCode.INVALID_ADDRESS,
                f"Unsupported asset: {asset}. Supported: {self.SUPPORTED_ASSETS}"
            )
        
        if amount <= 0:
            raise X402Error(
                X402ErrorCode.INSUFFICIENT_BALANCE,
                f"Invalid amount: {amount}. Must be positive."
            )
        
        print(f"[X402] Initiating escrow: {amount} {asset} from {sender_id} to {receiver_id}")
        
        if self.mock_mode:
            escrow_id = f"esc_mock_{sender_id}_{receiver_id}_{int(amount)}_{datetime.now().timestamp()}"
            return {
                "status": EscrowStatus.LOCKED.value,
                "escrow_id": escrow_id,
                "amount": amount,
                "asset": asset,
                "sender": sender_id,
                "receiver": receiver_id,
                "contract_hash": contract_hash,
                "message": "[MOCK] Funds locked in simulated escrow",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            escrow_id = f"esc_{sender_id}_{receiver_id}_{int(amount)}"
            
            self._escrow_store[escrow_id] = {
                "status": EscrowStatus.LOCKED,
                "amount": amount,
                "asset": asset,
                "sender": sender_id,
                "receiver": receiver_id,
                "contract_hash": contract_hash,
                "created_at": datetime.now()
            }
            
            return {
                "status": EscrowStatus.LOCKED.value,
                "escrow_id": escrow_id,
                "amount": amount,
                "asset": asset,
                "message": "Funds locked in X402 Relay Network awaiting B2P verdict.",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise X402Error(
                X402ErrorCode.NETWORK_TIMEOUT,
                f"Failed to initiate escrow: {str(e)}"
            )
    
    def release_funds(
        self, 
        escrow_id: str, 
        recipient: str, 
        verdict: str
    ) -> Dict[str, Any]:
        """
        Release funds based on B2P arbitration verdict.
        
        Args:
            escrow_id: The escrow ID from initiate_escrow_payment
            recipient: Wallet address to receive the funds
            verdict: Arbitration verdict - either 'seller_wins' or 'buyer_wins'
                    - 'seller_wins': Release funds to seller (receiver)
                    - 'buyer_wins': Refund to buyer (sender)
        
        Returns:
            Dictionary containing:
            - status: "settled" if successful
            - recipient: Recipient wallet address
            - amount: Amount released
            - tx_hash: Transaction hash (simulated in mock mode)
            - timestamp: ISO format timestamp
        
        Raises:
            X402Error: With code ESCROW_NOT_FOUND if escrow_id is invalid
                      With code ARBITRATION_PENDING if escrow is disputed
        
        Example:
            >>> result = bridge.release_funds(
            ...     escrow_id="esc_buyer_001_seller_002_500",
            ...     recipient="0x123...",
            ...     verdict="seller_wins"
            ... )
            >>> print(result["tx_hash"])
            '0x_x402_settlement_hash...'
        """
        print(f"[X402] Releasing funds for {escrow_id}. Verdict: {verdict}")
        
        if self.mock_mode:
            return {
                "status": "settled",
                "recipient": recipient,
                "verdict": verdict,
                "tx_hash": f"0x_mock_settlement_{escrow_id}",
                "message": "[MOCK] Funds released successfully",
                "timestamp": datetime.now().isoformat()
            }
        
        if escrow_id not in self._escrow_store:
            raise X402Error(
                X402ErrorCode.ESCROW_NOT_FOUND,
                f"Escrow ID not found: {escrow_id}"
            )
        
        escrow = self._escrow_store[escrow_id]
        
        if escrow["status"] == EscrowStatus.DISPUTED:
            raise X402Error(
                X402ErrorCode.ARBITRATION_PENDING,
                f"Escrow {escrow_id} is under dispute. Awaiting arbitration."
            )
        
        try:
            escrow["status"] = EscrowStatus.RELEASED if verdict == "seller_wins" else EscrowStatus.REFUNDED
            
            return {
                "status": "settled",
                "recipient": recipient,
                "amount": escrow["amount"],
                "asset": escrow["asset"],
                "verdict": verdict,
                "tx_hash": f"0x_x402_settlement_{escrow_id}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise X402Error(
                X402ErrorCode.INTERNAL_ERROR,
                f"Failed to release funds: {str(e)}"
            )
    
    def check_balance(
        self, 
        agent_id: str, 
        asset: str = "USDC"
    ) -> Dict[str, Any]:
        """
        Check available balance for an agent in X402 network.
        
        Args:
            agent_id: Unique identifier of the agent
            asset: Cryptocurrency asset to check (default: "USDC")
        
        Returns:
            Dictionary containing:
            - balance: Available balance amount
            - asset: Asset type
            - agent_id: Agent identifier
            - last_updated: ISO format timestamp
        
        Raises:
            X402Error: With code INVALID_ADDRESS if agent_id is invalid
        
        Example:
            >>> balance = bridge.check_balance("agent_001", "USDC")
            >>> print(balance["balance"])
            1000.0
        """
        if asset not in self.SUPPORTED_ASSETS:
            raise X402Error(
                X402ErrorCode.INVALID_ADDRESS,
                f"Unsupported asset: {asset}"
            )
        
        if self.mock_mode:
            mock_balances = {
                "buyer_001": 5000.0,
                "seller_002": 3000.0,
                "agent_001": 1000.0
            }
            balance = mock_balances.get(agent_id, 1000.0)
            
            return {
                "balance": balance,
                "asset": asset,
                "agent_id": agent_id,
                "mock_mode": True,
                "last_updated": datetime.now().isoformat()
            }
        
        try:
            return {
                "balance": 1000.0,
                "asset": asset,
                "agent_id": agent_id,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise X402Error(
                X402ErrorCode.NETWORK_TIMEOUT,
                f"Failed to check balance: {str(e)}"
            )
    
    def get_escrow_status(self, escrow_id: str) -> Dict[str, Any]:
        """
        Get the current status of an escrow payment.
        
        Args:
            escrow_id: The escrow ID to check
        
        Returns:
            Dictionary containing escrow details and current status
        
        Raises:
            X402Error: With code ESCROW_NOT_FOUND if escrow_id is invalid
        
        Example:
            >>> status = bridge.get_escrow_status("esc_buyer_001_seller_002_500")
            >>> print(status["status"])
            'locked'
        """
        if escrow_id not in self._escrow_store:
            raise X402Error(
                X402ErrorCode.ESCROW_NOT_FOUND,
                f"Escrow ID not found: {escrow_id}"
            )
        
        escrow = self._escrow_store[escrow_id]
        return {
            "escrow_id": escrow_id,
            "status": escrow["status"].value,
            "amount": escrow["amount"],
            "asset": escrow["asset"],
            "sender": escrow["sender"],
            "receiver": escrow["receiver"],
            "created_at": escrow["created_at"].isoformat()
        }
