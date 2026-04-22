import json
import random
import hashlib
import base64
from typing import List, Dict, Any
from config import Config

class ShardAlgorithm:
    def __init__(self, version: int, seed: str):
        self.version = version
        self.seed = seed + str(version)

    def shard(self, data: Dict[str, Any]) -> List[str]:
        json_str = json.dumps(data, sort_keys=True)
        chars = list(json_str)
        random.seed(self.seed)
        random.shuffle(chars)
        total = len(chars)
        size = total // Config.TOTAL_SHARDS
        shards = []

        for i in range(Config.TOTAL_SHARDS):
            start = i * size
            end = start + size if i < Config.TOTAL_SHARDS - 1 else total
            content = ''.join(chars[start:end])
            obfuscated = self._obfuscate(content, i)
            shards.append(obfuscated)

        return shards

    def reconstruct(self, fragments: List[str]) -> Dict[str, Any]:
        cleaned = []
        for i, frag in enumerate(fragments):
            content = self._deobfuscate(frag, i)
            cleaned.append(content)
        combined = ''.join(cleaned)
        return json.loads(combined)

    def _obfuscate(self, content: str, idx: int) -> str:
        prefix = hashlib.md5(f"{self.seed}_{idx}".encode()).hexdigest()[:8]
        suffix = hashlib.md5(f"{idx}_{self.seed}".encode()).hexdigest()[:8]
        encoded = base64.b64encode(content.encode()).decode()
        return f"v{self.version}_{prefix}_{encoded}_{suffix}"

    def _deobfuscate(self, obfuscated: str, idx: int) -> str:
        parts = obfuscated.split('_')
        if len(parts) >= 4:
            encoded = parts[2]
            return base64.b64decode(encoded).decode()
        return ""


def get_algorithm(version: int = None):
    if version is None:
        version = Config.CURRENT_ALGO_VERSION
    return ShardAlgorithm(version, Config.FOUNDER_WALLET)