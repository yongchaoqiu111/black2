import json
import os
import requests

class StorageAdapter:
    """
    B2P 存储适配器：管理信誉数据的读取与存证。
    支持 GitHub (人类可读) 和 IPFS (永久备份)。
    """

    def __init__(self, github_token=None, ipfs_host="http://127.0.0.1:5001"):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.ipfs_host = ipfs_host
        self.headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}

    def pull_repo_data(self, owner, repo, path="b2p-repo.json"):
        """
        从 GitHub 拉取最新的信誉数据。
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            content = response.json()["content"]
            import base64
            decoded = base64.b64decode(content).decode('utf-8')
            return json.loads(decoded)
        except Exception as e:
            print(f"[Storage] Pull failed: {e}")
            return None

    def push_to_github(self, owner, repo, path, data, message="Update B2P reputation"):
        """
        将更新后的信誉数据 Push 回 GitHub。
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        # 获取当前 SHA 以便更新
        current = self.pull_repo_data(owner, repo, path)
        sha = None
        if current:
            # 重新请求以获取 SHA
            resp = requests.get(url, headers=self.headers)
            sha = resp.json().get("sha")

        import base64
        payload = {
            "message": message,
            "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
        }
        if sha:
            payload["sha"] = sha

        try:
            resp = requests.put(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"[Storage] Push to GitHub failed: {e}")
            return False

    def upload_to_ipfs(self, data):
        """
        将数据上传至 IPFS 并返回 Hash。
        """
        try:
            files = {"file": json.dumps(data).encode()}
            response = requests.post(f"{self.ipfs_host}/api/v0/add", files=files)
            return response.json()["Hash"]
        except Exception as e:
            print(f"[Storage] IPFS upload failed: {e}")
            return None
