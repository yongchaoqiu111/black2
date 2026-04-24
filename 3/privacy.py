"""
Black2 Privacy Module - 隐私保护与数据脱敏
提供身份匿名、数据脱敏、零知识证明等功能
"""

import hashlib
import json
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PrivacyLevel(str, Enum):
    """隐私等级"""
    PUBLIC = "public"          # 完全公开
    AGGREGATED = "aggregated"  # 仅聚合数据
    ANONYMOUS = "anonymous"    # 匿名化
    ZKP = "zkp"               # 零知识证明


@dataclass
class AnonymousIdentity:
    """一次性匿名身份"""
    agent_id: str
    proxy_address: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    active: bool = True


class PrivacyManager:
    """隐私管理器"""
    
    def __init__(self):
        self.anonymous_identities: Dict[str, AnonymousIdentity] = {}
    
    def generate_proxy_address(self, real_address: str, salt: Optional[str] = None) -> str:
        """
        生成代理地址（一次性地址）
        
        Args:
            real_address: 真实钱包地址
            salt: 盐值，可选
            
        Returns:
            代理地址
        """
        if not salt:
            salt = str(uuid.uuid4())
        
        data = f"{real_address}:{salt}:{datetime.utcnow().isoformat()}"
        proxy_address = hashlib.sha256(data.encode()).hexdigest()[:42]  # 类似以太坊地址长度
        return proxy_address
    
    def create_anonymous_identity(self, agent_id: str, real_address: str, 
                                   ttl_hours: int = 24) -> AnonymousIdentity:
        """
        创建匿名身份
        
        Args:
            agent_id: AI Agent ID
            real_address: 真实钱包地址
            ttl_hours: 有效期（小时）
            
        Returns:
            匿名身份对象
        """
        proxy_address = self.generate_proxy_address(real_address)
        expires_at = None
        if ttl_hours > 0:
            from datetime import timedelta
            expires_dt = datetime.utcnow() + timedelta(hours=ttl_hours)
            expires_at = expires_dt.isoformat()
        
        identity = AnonymousIdentity(
            agent_id=agent_id,
            proxy_address=proxy_address,
            expires_at=expires_at
        )
        
        self.anonymous_identities[proxy_address] = identity
        return identity
    
    def deidentify_data(self, data: Dict[str, Any], 
                       privacy_level: PrivacyLevel = PrivacyLevel.AGGREGATED) -> Dict[str, Any]:
        """
        数据脱敏
        
        Args:
            data: 原始数据
            privacy_level: 隐私等级
            
        Returns:
            脱敏后的数据
        """
        result = data.copy()
        
        if privacy_level == PrivacyLevel.PUBLIC:
            return result
        
        # 移除敏感字段
        sensitive_fields = ['wallet_address', 'private_key', 'email', 'phone', 'real_name']
        for field in sensitive_fields:
            if field in result:
                del result[field]
        
        # 聚合化处理
        if privacy_level in [PrivacyLevel.AGGREGATED, PrivacyLevel.ANONYMOUS, PrivacyLevel.ZKP]:
            if 'transaction_history' in result:
                # 只保留聚合统计，移除具体交易
                history = result['transaction_history']
                result['total_transactions'] = len(history)
                result['total_volume'] = sum(t.get('amount', 0) for t in history)
                del result['transaction_history']
        
        # 匿名化处理
        if privacy_level in [PrivacyLevel.ANONYMOUS, PrivacyLevel.ZKP]:
            if 'agent_id' in result:
                result['agent_id'] = self._hash_identifier(result['agent_id'])
        
        return result
    
    def _hash_identifier(self, identifier: str) -> str:
        """哈希化标识符"""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def prepare_zkp_statement(self, data: Dict[str, Any], 
                             statement_type: str = "sufficient_reputation") -> Dict[str, Any]:
        """
        准备零知识证明声明
        
        Args:
            data: 信誉数据
            statement_type: 声明类型
            
        Returns:
            ZKP声明
        """
        if statement_type == "sufficient_reputation":
            return {
                "statement": "agent_has_sufficient_reputation",
                "min_score": 50.0,
                "actual_score": data.get("total_score", 0),
                "score_meets_threshold": data.get("total_score", 0) >= 50.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        elif statement_type == "no_recent_disputes":
            return {
                "statement": "no_recent_disputes",
                "dispute_count": data.get("dispute_count", 0),
                "clean_record": data.get("dispute_count", 0) == 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "statement": "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def verify_zkp_statement(self, statement: Dict[str, Any]) -> bool:
        """
        验证零知识证明声明（简化版）
        
        Args:
            statement: ZKP声明
            
        Returns:
            验证结果
        """
        if statement.get("statement") == "agent_has_sufficient_reputation":
            return statement.get("score_meets_threshold", False)
        elif statement.get("statement") == "no_recent_disputes":
            return statement.get("clean_record", False)
        return False


class PrivacyProtectedStorage:
    """隐私保护存储适配器"""
    
    def __init__(self, privacy_manager: PrivacyManager):
        self.privacy_manager = privacy_manager
    
    def sanitize_for_publication(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        净化数据以便公开发布
        
        Args:
            repo_data: 原始仓库数据
            
        Returns:
            净化后的数据
        """
        return self.privacy_manager.deidentify_data(
            repo_data, 
            privacy_level=PrivacyLevel.AGGREGATED
        )


# 单例实例
privacy_manager = PrivacyManager()
privacy_storage = PrivacyProtectedStorage(privacy_manager)
