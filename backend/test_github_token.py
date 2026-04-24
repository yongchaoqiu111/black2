import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_github_connection():
    token = os.getenv("ANCHOR_GITHUB_TOKEN")
    repo_url = os.getenv("ANCHOR_GITHUB_REPO_URL")
    
    # 解析 owner 和 repo
    parts = repo_url.rstrip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    
    print(f"Testing connection to: {owner}/{repo}")
    print(f"Using Token: {token[:10]}...")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # 1. 测试获取仓库信息
        try:
            resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=10)
            if resp.status_code == 200:
                print("✅ Repository access successful!")
                data = resp.json()
                print(f"   Default Branch: {data['default_branch']}")
            else:
                print(f"❌ Repository access failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Connection error: {e}")

        # 2. 测试 Gists 权限 (如果是用 Gist 存证)
        try:
            resp = await client.get("https://api.github.com/gists", headers=headers, timeout=10)
            if resp.status_code == 200:
                print("✅ Gists access successful!")
            else:
                print(f"❌ Gists access failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Gists connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_github_connection())
