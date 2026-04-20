"""
Anchor Service Module

Provides anchoring of transaction root hashes to GitHub Gist.
"""

import asyncio
import hashlib
import json
import httpx
import os
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AnchorService:
    def __init__(self, db):
        self.db = db
        self.github_token = os.getenv("ANCHOR_GITHUB_TOKEN", "")
        self.gist_id = os.getenv("ANCHOR_GITHUB_GIST_ID", "")

    def calculate_root_hash(self, transactions: list) -> str:
        if not transactions:
            return hashlib.sha256(b"empty").hexdigest()

        sorted_txs = sorted(transactions, key=lambda x: x["timestamp"])
        combined = "".join(tx["tx_hash"] for tx in sorted_txs)
        return hashlib.sha256(combined.encode()).hexdigest()

    async def anchor_to_gist(self, root_hash: str, transaction_count: int, previous_anchor: Optional[str]) -> dict:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "description": "Black2 Clearing Protocol - Transaction Anchor",
            "public": False,
            "files": {
                "anchor.json": {
                    "content": json.dumps({
                        "timestamp": timestamp,
                        "root_hash": root_hash,
                        "transaction_count": transaction_count,
                        "previous_anchor": previous_anchor or "",
                        "version": "1.0"
                    }, indent=2)
                }
            }
        }

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        async with httpx.AsyncClient() as client:
            if self.gist_id:
                response = await client.patch(
                    f"https://api.github.com/gists/{self.gist_id}",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
            else:
                response = await client.post(
                    "https://api.github.com/gists",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

            response.raise_for_status()
            data = response.json()
            return {
                "gist_url": data.get("html_url", ""),
                "gist_commit_hash": data.get("updated_at", "")
            }

    async def perform_anchor(self) -> Optional[dict]:
        transactions = await self.db.get_unanchored_transactions()

        if not transactions:
            return None

        root_hash = self.calculate_root_hash(transactions)
        previous_anchor = await self.db.get_latest_anchor()
        previous_anchor_hash = previous_anchor["root_hash"] if previous_anchor else None
        transaction_count = len(transactions)

        anchor_timestamp = datetime.now(timezone.utc).isoformat()

        result = await self.anchor_to_gist(root_hash, transaction_count, previous_anchor_hash)

        tx_hashes = [tx["tx_hash"] for tx in transactions]
        await self.db.anchor_transactions(tx_hashes, root_hash, anchor_timestamp)

        await self.db.add_anchor_record(
            root_hash=root_hash,
            transaction_count=transaction_count,
            gist_url=result["gist_url"],
            gist_commit_hash=result["gist_commit_hash"],
            anchor_timestamp=anchor_timestamp,
            previous_anchor=previous_anchor_hash
        )

        return {
            "root_hash": root_hash,
            "transaction_count": transaction_count,
            "gist_url": result["gist_url"],
            "gist_commit_hash": result["gist_commit_hash"],
            "anchor_timestamp": anchor_timestamp
        }