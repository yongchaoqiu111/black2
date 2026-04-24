# Black2 Anchor & Async Context

## 1. GitHub Anchor Service
**File:** `backend/src/anchor/github_anchor.py`
```python
class GithubAnchor:
    def push_commit(self, message, content):
        """
        将数据 Push 到 GitHub 仓库
        :param message: Commit 消息
        :param content: 文件内容 (JSON/Markdown)
        """
        # 现有逻辑：调用 GitHub API 进行 Push
        pass

    def get_latest_hash(self):
        """获取当前仓库最新的 Commit Hash"""
        pass
```

## 2. Async Task Handling
**File:** `backend/server.py`
```python
# 我们目前使用简单的 threading 或 asyncio 处理后台任务
import threading

def run_async_task(func, *args):
    thread = threading.Thread(target=func, args=args)
    thread.start()
```

## 3. Integration Requirement
*   **Goal:** When `GithubAnchor.push_commit` succeeds, we need to extract the commit hash and send it to X402 for on-chain anchoring.
*   **Constraint:** This operation must be non-blocking to ensure API response time < 200ms.
