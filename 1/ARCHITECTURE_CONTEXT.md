# Black2 Backend Core Context (For X402 Integration)

## 1. Database Schema (SQLite)
**File:** `backend/src/db/transaction_db.py`
```python
# 现有交易表结构（简化版）
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash TEXT UNIQUE,
    buyer_address TEXT,
    seller_address TEXT,
    amount REAL,
    status TEXT, -- 'pending', 'completed', 'disputed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
# TODO: 需要增加 x402_escrow_id 字段
```

## 2. Arbitration Logic Hook
**File:** `backend/src/anchor/arbitration_timer.py`
```python
def execute_arbitration_verdict(tx_id, verdict):
    """
    仲裁裁决执行函数
    :param tx_id: 交易ID
    :param verdict: 'buyer_wins' 或 'seller_wins'
    """
    # 1. 更新本地数据库状态
    update_transaction_status(tx_id, verdict)
    
    # 2. [HOOK] 此处应调用 X402Bridge 释放资金
    # x402_bridge.release_funds(...)
    
    # 3. 更新 Git 锚点记录
    github_anchor.push_verdict(tx_id, verdict)
```

## 3. Wallet System
**File:** `backend/src/crypto/hd_wallet.py`
```python
class HDWallet:
    def get_private_key(self, path="m/44'/60'/0'/0/0"):
        """获取指定路径的私钥用于签名"""
        pass
    
    def sign_transaction(self, data, private_key):
        """使用私钥对数据进行签名"""
        pass
```

## 4. API Routes
**File:** `backend/src/api/routes.py`
```python
@app.route('/api/v1/transactions/create', methods=['POST'])
def create_transaction():
    """
    创建交易接口
    需要在返回结果中包含 X402 托管地址
    """
    pass
```
