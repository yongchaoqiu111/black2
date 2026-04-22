import os
import json
import requests
from typing import List, Dict
from config import Config

class DistributedStorage:
    def __init__(self):
        self.shard_map = {}

    def store(self, data_id: str, shards: List[str]) -> Dict[int, List[str]]:
        locations = {}
        for i, shard in enumerate(shards):
            shard_locations = []
            for replica in range(Config.REPLICA_COUNT):
                node = Config.STORAGE_NODES[(i + replica) % len(Config.STORAGE_NODES)]
                location = self._upload_to_node(shard, node, i)
                shard_locations.append(location)
            locations[i] = shard_locations
        self.shard_map[data_id] = locations
        return locations

    def retrieve(self, data_id: str) -> List[str]:
        locations = self.shard_map.get(data_id)
        if not locations:
            raise ValueError(f"Data {data_id} not found")
        fragments = []
        for i in range(Config.TOTAL_SHARDS):
            shard_locations = locations.get(i, [])
            fragment = None
            for loc in shard_locations:
                fragment = self._download_from_node(loc)
                if fragment:
                    break
            if fragment is None:
                raise ValueError(f"Shard {i} for {data_id} not available")
            fragments.append(fragment)
        return fragments

    def _upload_to_node(self, shard: str, node: Dict, idx: int) -> str:
        if node["name"] == "local":
            path = f"{node['path']}shard_{idx}_{hash(shard)}.txt"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(shard)
            return f"local://{path}"
        elif node["name"] == "ipfs":
            try:
                response = requests.post(node["url"], files={"file": shard.encode()})
                if response.status_code == 200:
                    hash_val = response.json().get("Hash")
                    return f"ipfs://{hash_val}"
            except:
                pass
            return f"ipfs://fallback_{hash(shard)}"
        elif node["name"] == "github":
            return f"github://{hash(shard)}"
        return f"unknown://{hash(shard)}"

    def _download_from_node(self, location: str) -> str:
        if location.startswith("local://"):
            path = location[8:]
            with open(path, "r") as f:
                return f.read()
        elif location.startswith("ipfs://"):
            return "mock_shard_content"
        return None


storage = DistributedStorage()