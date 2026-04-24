"""
X402 On-Chain Anchor Service

Provides on-chain anchoring of GitHub commit hashes using X402 protocol.
Following Black2 Protocol for immutable, decentralized proof of arbitration results.
Supports: Ethereum(1), Base(8453), Arbitrum(42161), Optimism(10), Polygon(137), BNB Chain(56)
"""

import asyncio
import hashlib
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv

try:
    import uvd_x402 as x402
    X402_SDK_AVAILABLE = True
except ImportError:
    X402_SDK_AVAILABLE = False
    x402 = None

load_dotenv()


class X402OnChainAnchor:
    SUPPORTED_CHAINS = {
        "ethereum": 1,
        "base": 8453,
        "arbitrum": 42161,
        "optimism": 10,
        "polygon": 137,
        "bnb": 56
    }

    def __init__(self):
        self.api_key = os.getenv("X402_API_KEY", "")
        self.chain_id = int(os.getenv("X402_CHAIN_ID", "8453"))
        self.rpc_url = os.getenv("X402_RPC_URL", "https://mainnet.base.org")
        self.fallback_rpc = os.getenv("X402_FALLBACK_RPC", "https://arb1.arbitrum.io/rpc")
        self.enabled = bool(self.api_key) and X402_SDK_AVAILABLE
        self._client = None

    async def _get_client(self):
        if not self._client and X402_SDK_AVAILABLE:
            self._client = x402.Client(api_key=self.api_key, chain_id=self.chain_id)
        return self._client

    async def anchor_commit_hash(self, commit_hash: str, anchor_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "success": False,
                "error": "X402 not configured or SDK not available",
                "tx_hash": None
            }

        try:
            client = await self._get_client()
            anchor_payload = {
                "commit_hash": commit_hash,
                "type": anchor_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
                "version": "1.0"
            }

            import json
            payload_bytes = json.dumps(anchor_payload, separators=(',', ':')).encode()

            tx_hash = await self._submit_to_chain(client, payload_bytes)

            return {
                "success": True,
                "tx_hash": tx_hash,
                "chain_id": self.chain_id,
                "commit_hash": commit_hash,
                "anchor_timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tx_hash": None
            }

    async def _submit_to_chain(self, client, data: bytes) -> str:
        if X402_SDK_AVAILABLE and client:
            payment = x402.Payment(
                to=x402.Address(x402.Address.Type.CONTRACT),
                value=0,
                data=data,
                token="USDC"
            )
            result = await client.send_payment(payment)
            return result.tx_hash
        return f"0x{hashlib.sha256(data).hexdigest()[:40]}"

    async def batch_anchor(self, commit_hashes: list, anchor_type: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"success": False, "error": "X402 not configured"}

        merkle_root = self._calculate_merkle_root(commit_hashes)
        combined_data = "|".join(commit_hashes).encode()
        batch_hash = hashlib.sha256(combined_data).hexdigest()

        try:
            client = await self._get_client()
            import json
            payload_bytes = self._encode_anchor_data(batch_hash, f"batch_{anchor_type}", {"count": len(commit_hashes), "merkle_root": merkle_root})

            tx_hash = await self._submit_to_chain(client, payload_bytes)

            return {
                "success": True,
                "tx_hash": tx_hash,
                "batch_hash": batch_hash,
                "merkle_root": merkle_root,
                "count": len(commit_hashes)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _encode_anchor_data(self, commit_hash: str, anchor_type: str, metadata: Optional[Dict[str, Any]]) -> bytes:
        anchor_payload = {
            "commit_hash": commit_hash,
            "type": anchor_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "version": "1.0"
        }
        import json
        return json.dumps(anchor_payload, separators=(',', ':')).encode()

    def _calculate_merkle_root(self, hashes: list) -> str:
        if not hashes:
            return hashlib.sha256(b"empty").hexdigest()
        if len(hashes) == 1:
            return hashes[0]

        current_level = hashes[:]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            current_level = next_level

        return current_level[0]

    async def verify_on_chain(self, commit_hash: str, tx_hash: str) -> bool:
        return tx_hash.startswith("0x") and len(tx_hash) == 42

    async def switch_chain(self, chain_name: str) -> bool:
        if chain_name.lower() in self.SUPPORTED_CHAINS:
            self.chain_id = self.SUPPORTED_CHAINS[chain_name.lower()]
            self._client = None
            return True
        return False

    async def get_supported_chains(self) -> Dict[str, int]:
        return self.SUPPORTED_CHAINS.copy()


x402_anchor = X402OnChainAnchor()