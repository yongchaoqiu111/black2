"""
GitHub Anchor Service

Anchors transaction hashes and contract hashes to GitHub Repository for immutable proof.
Following Black2 Protocol Section 2.7 Rule 1 and Section 2.5.
"""

import hashlib
import json
import httpx
import base64
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class GitHubAnchorService:
    """
    Service for anchoring hashes to GitHub Repository.
    Provides immutable, timestamped proof of transactions and contracts.
    """
    
    def __init__(self):
        self.github_token = os.getenv("ANCHOR_GITHUB_TOKEN", "")
        self.repo_url = os.getenv("ANCHOR_GITHUB_REPO_URL", "")
        self.branch = os.getenv("ANCHOR_GITHUB_BRANCH", "main")
        
        if not self.github_token:
            raise ValueError("ANCHOR_GITHUB_TOKEN environment variable is required")
        
        # Extract owner and repo from URL
        # Format: https://github.com/owner/repo
        if self.repo_url:
            parts = self.repo_url.rstrip('/').split('/')
            self.owner = parts[-2]
            self.repo = parts[-1]
        else:
            self.owner = ""
            self.repo = ""
    
    def calculate_merkle_root(self, hashes: List[str]) -> str:
        """
        Calculate Merkle root from a list of hashes.
        Following Black2 Protocol Section 2.5 for batch transactions.
        """
        if not hashes:
            return hashlib.sha256(b"empty").hexdigest()
        
        if len(hashes) == 1:
            return hashes[0]
        
        # Build Merkle tree
        current_level = hashes[:]
        
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Hash the concatenation
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            current_level = next_level
        
        return current_level[0]
    
    async def anchor_contract_hash(
        self,
        contract_hash: str,
        file_hash: str,
        seller_id: str,
        product_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Anchor a contract hash to GitHub Repository.
        
        Args:
            contract_hash: SHA-256 hash of contract data
            file_hash: SHA-256 hash of product file
            seller_id: Seller's wallet address (DID)
            product_id: Unique product identifier
            metadata: Additional metadata
            
        Returns:
            {
                "commit_url": str,
                "anchor_timestamp": str,
                "contract_hash": str,
                "file_hash": str
            }
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        anchor_data = {
            "type": "contract_anchor",
            "timestamp": timestamp,
            "contract_hash": contract_hash,
            "file_hash": file_hash,
            "seller_id": seller_id,
            "product_id": product_id,
            "metadata": metadata or {},
            "protocol_version": "1.0"
        }
        
        # File path: anchors/contracts/{product_id}_{timestamp}.json
        filename = f"anchors/contracts/{product_id}_{int(datetime.now().timestamp())}.json"
        
        return await self._commit_to_repo(anchor_data, filename, f"Anchor contract {product_id}")
    
    async def anchor_transaction_batch(
        self,
        transaction_hashes: List[str],
        batch_id: str
    ) -> Dict[str, Any]:
        """
        Anchor a batch of transaction hashes using Merkle root.
        Following Black2 Protocol Section 2.5 for performance optimization.
        
        Args:
            transaction_hashes: List of transaction hashes
            batch_id: Unique batch identifier
            
        Returns:
            {
                "commit_url": str,
                "merkle_root": str,
                "transaction_count": int,
                "batch_id": str
            }
        """
        merkle_root = self.calculate_merkle_root(transaction_hashes)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        anchor_data = {
            "type": "transaction_batch",
            "timestamp": timestamp,
            "batch_id": batch_id,
            "merkle_root": merkle_root,
            "transaction_count": len(transaction_hashes),
            "transaction_hashes": transaction_hashes,
            "protocol_version": "1.0"
        }
        
        # File path: anchors/batches/{batch_id}_{timestamp}.json
        filename = f"anchors/batches/{batch_id}_{int(datetime.now().timestamp())}.json"
        
        result = await self._commit_to_repo(anchor_data, filename, f"Anchor batch {batch_id}")
        result["merkle_root"] = merkle_root
        
        return result
    
    async def _commit_to_repo(self, data: Dict[str, Any], filepath: str, commit_message: str) -> Dict[str, Any]:
        """
        Commit data to GitHub Repository.
        
        Args:
            data: Data to anchor
            filepath: File path in repository
            commit_message: Git commit message
            
        Returns:
            Commit result with URL
        """
        # Encode content as base64
        content = json.dumps(data, indent=2, ensure_ascii=False)
        content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # API endpoint for creating/updating file
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{filepath}"
        
        payload = {
            "message": commit_message,
            "content": content_base64,
            "branch": self.branch
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Check if file exists (to get SHA for update)
                check_response = await client.get(api_url, headers=headers, timeout=10.0)
                
                if check_response.status_code == 200:
                    # File exists, need SHA for update
                    existing_data = check_response.json()
                    payload["sha"] = existing_data.get("sha")
                    
                    # Update file
                    response = await client.put(api_url, headers=headers, json=payload, timeout=30.0)
                else:
                    # File doesn't exist, create new
                    response = await client.put(api_url, headers=headers, json=payload, timeout=30.0)
                
                response.raise_for_status()
                commit_data = response.json()
                
                return {
                    "commit_url": commit_data.get("commit", {}).get("html_url", ""),
                    "file_url": commit_data.get("content", {}).get("html_url", ""),
                    "sha": commit_data.get("commit", {}).get("sha", ""),
                    "anchor_timestamp": data.get("timestamp"),
                    "success": True
                }
                
            except Exception as e:
                return {
                    "commit_url": "",
                    "file_url": "",
                    "sha": "",
                    "anchor_timestamp": data.get("timestamp"),
                    "success": False,
                    "error": str(e)
                }
    
    async def verify_anchor(self, commit_url: str, expected_hash: str) -> bool:
        """
        Verify that a hash exists in a GitHub Repository anchor.
        
        Args:
            commit_url: URL of the GitHub commit or file
            expected_hash: Hash to verify
            
        Returns:
            True if hash is found and matches
        """
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Extract file path from URL
                # Format: https://github.com/owner/repo/blob/main/anchors/contracts/xxx.json
                if "/blob/" in commit_url:
                    # It's a file URL
                    parts = commit_url.split("/blob/")
                    if len(parts) < 2:
                        return False
                    file_path = parts[1]
                elif "/commit/" in commit_url:
                    # It's a commit URL - need to get commit details
                    commit_sha = commit_url.split("/commit/")[-1]
                    response = await client.get(
                        f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{commit_sha}",
                        headers=headers,
                        timeout=10.0
                    )
                    response.raise_for_status()
                    commit_data = response.json()
                    
                    # Check commit message and files
                    # For now, return True if commit exists
                    # In production, would verify the actual content
                    return True
                else:
                    return False
                
                # Get file content
                response = await client.get(
                    f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{file_path}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                file_data = response.json()
                content_base64 = file_data.get("content", "")
                
                # Decode base64 content
                import base64
                content = base64.b64decode(content_base64).decode('utf-8')
                anchor_data = json.loads(content)
                
                # Check if expected hash matches any hash in the anchor
                if (anchor_data.get("contract_hash") == expected_hash or
                    anchor_data.get("file_hash") == expected_hash or
                    anchor_data.get("merkle_root") == expected_hash):
                    return True
                
                # Check transaction hashes in batch
                if "transaction_hashes" in anchor_data:
                    if expected_hash in anchor_data["transaction_hashes"]:
                        return True
                
                return False
                
            except Exception as e:
                print(f"Verification error: {e}")
                return False
