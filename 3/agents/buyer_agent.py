import httpx
import json
import hashlib
import time
import nacl.signing
from nacl.encoding import HexEncoder

class BuyerAgent:
    def __init__(self, config):
        self.address = config['buyer']['address']
        self.private_key = config['buyer']['private_key']
        self.api_base_url = config['buyer']['api_base_url']
    
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
    
    def create_transaction(self, to_address, amount, contract_content):
        contract_hash = self.sha256_hash(contract_content)
        
        tx_data = {
            "from_address": self.address,
            "to_address": to_address,
            "amount": amount,
            "currency": "USDT",
            "contract_hash": contract_hash
        }
        
        signature = self.sign_request(tx_data)
        
        headers = {
            "X-Public-Key": self.address,
            "X-Signature": signature
        }
        
        url = f"{self.api_base_url}/api/v1/transactions"
        response = httpx.post(url, json=tx_data, headers=headers)
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
    
    def initiate_dispute(self, tx_id, reason):
        data = {"reason": reason}
        
        signature = self.sign_request(data)
        
        headers = {
            "X-Public-Key": self.address,
            "X-Signature": signature
        }
        
        url = f"{self.api_base_url}/api/v1/transactions/{tx_id}/dispute"
        response = httpx.post(url, json=data, headers=headers)
        return response.json()
    
    def run(self, seller_address, amount, contract_content):
        print("=== 买家代理开始运行 ===")
        
        # 1. 创建交易
        print("正在创建交易...")
        tx_response = self.create_transaction(seller_address, amount, contract_content)
        tx_id = tx_response.get('tx_id')
        print(f"交易创建成功，交易ID: {tx_id}")
        
        # 2. 监听交易状态
        print("正在监听交易状态...")
        while True:
            time.sleep(2)
            tx = self.get_transaction(tx_id)
            status = tx.get('status')
            print(f"当前状态: {status}")
            
            if status == 'delivered':
                print("卖家已交付，正在验证...")
                file_hash = tx.get('file_hash')
                contract_hash = tx.get('contract_hash')
                
                # 3. 验证交付物
                if file_hash == contract_hash:
                    print("验证通过，确认收货...")
                    self.update_transaction_status(tx_id, 'completed')
                    print("交易完成！")
                else:
                    print("验证失败，发起纠纷...")
                    self.initiate_dispute(tx_id, "File hash does not match contract")
                    print("纠纷已发起！")
                break
            elif status in ['completed', 'disputed', 'refunded']:
                print(f"交易已结束，状态: {status}")
                break

if __name__ == "__main__":
    # 加载配置
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # 示例合同内容
    contract_content = {
        "task": "write article",
        "word_count": 100,
        "topic": "AI agents"
    }
    
    # 运行买家代理
    buyer = BuyerAgent(config)
    buyer.run(
        seller_address=config['seller']['address'],
        amount=100.00,
        contract_content=contract_content
    )