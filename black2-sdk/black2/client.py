from .reputation import ReputationEngine
from .storage import StorageAdapter
from .models import ReputationData, RiskLevel
import json

class B2PClient:
    """
    Black2 Protocol 客户端：AI 交易信任层的统一入口。
    """

    def __init__(self, github_token=None, ipfs_host="http://127.0.0.1:5001", local_mode=False):
        self.engine = ReputationEngine()
        if local_mode:
            # 使用本地文件存储进行调试
            from pathlib import Path
            self.storage = type('LocalStorage', (), {
                'pull_reputation': lambda self, agent_id: self._load_local(agent_id),
                'push_reputation': lambda self, agent_id, data: self._save_local(agent_id, data)
            })()
            self.workspace = Path("./b2p_data")
            self.workspace.mkdir(exist_ok=True)
        else:
            self.storage = StorageAdapter(github_token=github_token, ipfs_host=ipfs_host)

    def _load_local(self, agent_id):
        repo_path = self.workspace / f"{agent_id}.json"
        if not repo_path.exists():
            return None
        with open(repo_path, 'r') as f:
            data = json.load(f)
        return ReputationData(**data)

    def _save_local(self, agent_id, data):
        repo_path = self.workspace / f"{agent_id}.json"
        with open(repo_path, 'w') as f:
            json.dump(data.__dict__, f, indent=2, default=str)

    def check_agent_risk(self, agent_id, github_owner=None, github_repo=None):
        """
        查询指定 AI Agent 的风险等级。
        """
        print(f"[B2P] Checking risk for {agent_id}...")
        
        # 兼容旧版 GitHub 模式和新版 Local/GitHub 模式
        if github_owner and github_repo:
            repo_data = self.storage.pull_repo_data(github_owner, github_repo)
        else:
            repo_data = self.storage.pull_reputation(agent_id)
        
        if not repo_data:
            return {"error": "Repo data not found or invalid", "risk_level": RiskLevel.CRITICAL}

        assessment = {
            "risk_level": self.engine.get_risk_level(repo_data),
            "friction_coefficient": self.engine.calculate_friction_coefficient(repo_data),
            "total_score": repo_data.total_score
        }
        return assessment

    def record_transaction(self, agent_id, success: bool, amount: float, 
                           was_disputed: bool = False, dispute_won: bool = False,
                           github_owner=None, github_repo=None):
        """
        记录一笔交易结果并更新信誉仓库。
        """
        print(f"[B2P] Recording transaction for {agent_id}...")
        
        if github_owner and github_repo:
            repo_data = self.storage.pull_repo_data(github_owner, github_repo)
        else:
            repo_data = self.storage.pull_reputation(agent_id)
        
        if not repo_data:
            # 如果是新用户，初始化数据
            repo_data = ReputationData(agent_id=agent_id)
        
        # 调用引擎更新信誉
        updated_data = self.engine.update_reputation(
            repo_data, success, amount, was_disputed, dispute_won
        )
        
        # 保存回存储
        if github_owner and github_repo:
            self.storage.push_to_github(github_owner, github_repo, "b2p-repo.json", updated_data.__dict__)
        else:
            self.storage.push_reputation(agent_id, updated_data)
            
        return {"success": True, "new_score": updated_data.total_score}
