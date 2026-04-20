import httpx
import json
import hashlib
import time
import nacl.signing
from nacl.encoding import HexEncoder

class SellerAgent:
    def __init__(self, config):
        self.address = config['seller']['address']
        self.private_key = config['seller']['private_key']
        self.api_base_url = config['seller']['api_base_url']
    
    def sha256_hash(self, data):
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(data_bytes).hexdigest()
    
    def sign_request(self, data):
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        hash_hex = self.sha256_hash(json_str)
        
        signing_key = nacl.signing.SigningKey(self.private_key.encode(), encoder=HexEncoder)
        signature = signing_key.sign(hash_hex.encode()).signature.hex()
        
        return signature
    
    def get_pending_transactions(self):
        url = f"{self.api_base_url}/api/v1/transactions?to_address={self.address}&status=pending"
        response = httpx.get(url)
        return response.json()
    
    def get_transaction(self, tx_id):
        url = f"{self.api_base_url}/api/v1/transactions/{tx_id}"
        response = httpx.get(url)
        return response.json()
    
    def update_transaction_status(self, tx_id, status, file_hash=None):
        data = {"status": status}
        if file_hash:
            data["file_hash"] = file_hash
        
        signature = self.sign_request(data)
        
        headers = {
            "X-Public-Key": self.address,
            "X-Signature": signature
        }
        
        url = f"{self.api_base_url}/api/v1/transactions/{tx_id}/status"
        response = httpx.put(url, json=data, headers=headers)
        return response.json()
    
    def get_wallet_balance(self):
        url = f"{self.api_base_url}/api/v1/wallet/{self.address}"
        response = httpx.get(url)
        return response.json()
    
    def generate_delivery(self, contract_hash):
        # 这里简化处理，实际应该根据contract_hash生成对应的交付物
        # 为了演示，直接返回contract_hash作为file_hash
        return contract_hash
    
    def run(self):
        print("=== 卖家代理开始运行 ===")
        
        while True:
            print("正在查询新订单...")
            
            # 1. 查询待处理订单
            pending_tx = self.get_pending_transactions()
            transactions = pending_tx.get('transactions', [])
            
            if transactions:
                for tx in transactions:
                    tx_id = tx.get('tx_id')
                    print(f"发现新订单: {tx_id}")
                    
                    # 获取详细交易信息
                    tx_detail = self.get_transaction(tx_id)
                    contract_hash = tx_detail.get('contract_hash')
                    
                    # 2. 生成交付物
                    print("正在生成交付物...")
                    file_hash = self.generate_delivery(contract_hash)
                    
                    # 3. 提交交付
                    print("正在提交交付...")
                    self.update_transaction_status(tx_id, 'delivered', file_hash)
                    print(f"交付成功，交易ID: {tx_id}")
                    
                    # 4. 等待收款
                    print("正在等待收款...")
                    while True:
                        time.sleep(2)
                        updated_tx = self.get_transaction(tx_id)
                        status = updated_tx.get('status')
                        print(f"当前状态: {status}")
                        
                        if status == 'completed':
                            print("交易完成，正在查询余额...")
                            balance = self.get_wallet_balance()
                            print(f"钱包余额: {balance}")
                            break
                        elif status in ['disputed', 'refunded']:
                            print(f"交易异常，状态: {status}")
                            break
            else:
                print("暂无新订单，2秒后重试...")
                time.sleep(2)

if __name__ == "__main__":
    # 加载配置
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # 运行卖家代理
    seller = SellerAgent(config)
    seller.run()