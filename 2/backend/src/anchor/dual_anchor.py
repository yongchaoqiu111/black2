"""
Dual Anchor Service

Integrates GitHub anchor with X402 on-chain anchor for enhanced proof of arbitration results.
Following Black2 Protocol: GitHub as primary public ledger, X402 as supplementary verification layer.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DualAnchorService:
    def __init__(self, github_anchor, x402_anchor):
        self.github_anchor = github_anchor
        self.x402_anchor = x402_anchor
        self._pending_chain_anchors = []

    async def anchor_arbitration_result(
        self,
        arbitration_id: str,
        verdict: str,
        commit_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = {
            "arbitration_id": arbitration_id,
            "verdict": verdict,
            "github_commit_hash": commit_hash,
            "x402_tx_hash": None,
            "x402_success": False,
            "dual_anchor_timestamp": datetime.now(timezone.utc).isoformat()
        }

        x402_result = await self.x402_anchor.anchor_commit_hash(
            commit_hash=commit_hash,
            anchor_type="arbitration",
            metadata={
                "arbitration_id": arbitration_id,
                "verdict": verdict,
                **(metadata or {})
            }
        )

        result["x402_tx_hash"] = x402_result.get("tx_hash")
        result["x402_success"] = x402_result.get("success", False)
        result["x402_error"] = x402_result.get("error")

        if x402_result.get("success"):
            logger.info(f"X402 anchor success for arbitration {arbitration_id}: {x402_result.get('tx_hash')}")
        else:
            logger.warning(f"X402 anchor failed for arbitration {arbitration_id}: {x402_result.get('error')}")
            self._pending_chain_anchors.append({
                "commit_hash": commit_hash,
                "anchor_type": "arbitration",
                "metadata": metadata,
                "retry_count": 0
            })

        return result

    async def anchor_batch_with_x402(
        self,
        transaction_hashes: list,
        batch_id: str,
        github_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        commit_hash = github_result.get("sha", "")

        x402_result = await self.x402_anchor.batch_anchor(
            commit_hashes=transaction_hashes,
            anchor_type="transaction_batch"
        )

        return {
            "batch_id": batch_id,
            "github_commit_hash": commit_hash,
            "github_commit_url": github_result.get("commit_url", ""),
            "x402_batch_tx_hash": x402_result.get("tx_hash"),
            "x402_success": x402_result.get("success", False),
            "merkle_root": x402_result.get("merkle_root"),
            "transaction_count": len(transaction_hashes)
        }

    async def retry_pending_chain_anchors(self):
        if not self._pending_chain_anchors:
            return

        logger.info(f"Retrying {len(self._pending_chain_anchors)} pending X402 anchors")

        remaining = []
        for pending in self._pending_chain_anchors:
            if pending["retry_count"] >= 3:
                logger.warning(f"Max retries reached for pending anchor: {pending['commit_hash']}")
                continue

            result = await self.x402_anchor.anchor_commit_hash(
                commit_hash=pending["commit_hash"],
                anchor_type=pending["anchor_type"],
                metadata=pending["metadata"]
            )

            if result.get("success"):
                logger.info(f"Retry successful for {pending['commit_hash']}")
            else:
                pending["retry_count"] += 1
                remaining.append(pending)

        self._pending_chain_anchors = remaining

    async def get_pending_count(self) -> int:
        return len(self._pending_chain_anchors)
