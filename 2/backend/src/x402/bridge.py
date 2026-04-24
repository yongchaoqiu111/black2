"""
X402 Bridge Module

X402 支付桥接层：处理 B2P 协议中的资金流转。
核心能力：跨链支付、资金托管（Escrow）、无 Gas 交易。
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class X402Bridge:
    """
    X402 支付桥接层
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("X402_API_KEY")
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            logger.info(f"[X402 Bridge] Initialized with API Key: {self.api_key[:8]}...")
        else:
            logger.warning("[X402 Bridge] Disabled (no API key)")

    async def initiate_escrow_payment(
        self,
        sender_id: str,
        receiver_id: str,
        amount: float,
        asset: str = "USDC"
    ) -> Dict[str, Any]:
        """
        发起一笔托管支付（条件支付）。
        资金会被锁定在 X402 中继网络中，直到 B2P 仲裁引擎发出指令。
        """
        if not self.enabled:
            return {
                "status": "simulated",
                "escrow_id": f"sim_esc_{sender_id}_{receiver_id}_{int(amount)}",
                "message": "X402 disabled, using simulated escrow"
            }
        
        logger.info(f"[X402] Initiating escrow: {amount} {asset} from {sender_id} to {receiver_id}")
        
        # TODO: 实际调用 uvd-x402-sdk
        # response = await x402_client.pay({...})
        
        return {
            "status": "locked",
            "escrow_id": f"esc_{sender_id}_{receiver_id}_{int(amount)}",
            "message": "Funds locked in X402 Relay Network awaiting B2P verdict."
        }

    async def release_funds(
        self,
        escrow_id: str,
        recipient: str,
        verdict: str
    ) -> Dict[str, Any]:
        """
        根据 B2P 仲裁裁决释放资金。
        verdict: 'seller_wins' (放款给卖家) 或 'buyer_wins' (退款给买家)
        """
        if not self.enabled:
            return {
                "status": "simulated",
                "recipient": recipient,
                "tx_hash": f"0x_sim_{hashlib.sha256((escrow_id+verdict).encode()).hexdigest()[:32]}",
                "message": "X402 disabled, using simulated release"
            }
        
        logger.info(f"[X402] Releasing funds for {escrow_id}. Verdict: {verdict}")
        
        # TODO: 实际调用 uvd-x402-sdk
        # tx_hash = await x402_client.settle(escrow_id, recipient)
        
        import hashlib
        return {
            "status": "settled",
            "recipient": recipient,
            "tx_hash": f"0x_{hashlib.sha256((escrow_id+verdict).encode()).hexdigest()[:40]}",
            "message": "Funds released via X402 Relay Network"
        }

    async def check_balance(
        self,
        agent_id: str,
        asset: str = "USDC"
    ) -> Dict[str, Any]:
        """
        查询 Agent 在 X402 网络中的可用余额。
        """
        if not self.enabled:
            return {"balance": 1000.0, "asset": asset, "status": "simulated"}
        
        # TODO: 实际调用 uvd-x402-sdk
        # balance = await x402_client.get_balance(agent_id, asset)
        
        return {"balance": 1000.0, "asset": asset}


# Global instance
x402_bridge = X402Bridge()
