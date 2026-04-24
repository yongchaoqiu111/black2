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
        """
        Calculate Merkle Root Hash for a batch of transactions.
        If no transactions, return empty hash.
        """
        if not transactions:
            return hashlib.sha256(b"empty").hexdigest()

        # Extract and sort transaction hashes
        tx_hashes = [hashlib.sha256(tx["tx_hash"].encode()).hexdigest() for tx in transactions]
        tx_hashes.sort()

        # Build Merkle Tree
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])  # Duplicate last hash if odd number
            
            next_level = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i+1]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            
            tx_hashes = next_level

        return tx_hashes[0]

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
        from src.anchor.github_anchor import GitHubAnchorService
        
        transactions = await self.db.get_unanchored_transactions()
        if not transactions:
            return None

        # Extract hashes for Merkle Root calculation
        tx_hashes = [tx['tx_hash'] for tx in transactions]
        
        try:
            anchor_svc = GitHubAnchorService()
            batch_id = f"BATCH_{int(datetime.now(timezone.utc).timestamp())}"
            
            result = await anchor_svc.anchor_batch_transactions(
                transaction_hashes=tx_hashes,
                batch_id=batch_id
            )
            
            # Mark transactions as anchored in DB
            await self.db.anchor_transactions(tx_hashes, result['merkle_root'], result['anchor_timestamp'])
            
            return {
                "root_hash": result['merkle_root'],
                "transaction_count": result['transaction_count'],
                "gist_url": result['commit_url'],
                "gist_commit_hash": result['commit_sha'],
                "anchor_timestamp": result['anchor_timestamp']
            }
        except Exception as e:
            print(f"[Anchor] Failed to push to GitHub: {e}")
            return None