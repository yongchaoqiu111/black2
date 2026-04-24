import requests
import json
import hashlib

BASE_URL = "http://localhost:3000"

def test_micro_transaction_flow():
    # 0. 注册卖家账号
    print("--- 0. 注册测试用卖家 AI ---")
    seller_address = "TTestSeller123456789"
    
    # Step 1: Register
    register_payload = {
        "email": "seller@test.com",
        "password": "123456",
        "address": seller_address,  # This will be overwritten by verify-email logic
        "username": "AI_Seller_Bot",
        "role": "seller"
    }
    reg_res = requests.post(f"{BASE_URL}/api/v1/users/register", json=register_payload).json()
    code = reg_res.get('mockCode')
    
    # Step 2: Verify (This generates the actual AI address)
    verify_payload = {
        "email": "seller@test.com",
        "code": str(code),
        "referrer_address": seller_address # Pass our desired AI address as referrer to trick it into using it?
    }
    verify_res = requests.post(f"{BASE_URL}/api/v1/users/verify-email", json=verify_payload).json()
    
    # Get the generated AI address from the verification response
    if 'ai_address' in verify_res:
        seller_address = verify_res['ai_address']
        print(f"Generated AI Address: {seller_address}")
    
    print("\n--- 1. 模拟卖家 AI 发布微交易商品 ---")
    
    # 准备一个虚拟的交付物哈希 (比如一段代码的 SHA-256)
    dummy_code = "print('Hello Black2 Micro-Transaction')"
    delivery_hash = hashlib.sha256(dummy_code.encode()).hexdigest()
    
    seller_payload = {
        "seller_address": seller_address,
        "name": "USDT Auto Transfer Bot v1.0",
        "description": "Automated script for hourly USDT transfers.",
        "price": 0.001,
        "currency": "TRX",
        "category_id": "software/automation/bot",
        "delivery_hash": delivery_hash,
        "specs": {
            "runtime": "python_3.10",
            "delivery_type": "source_code",
            "metrics": {
                "latency_ms": 150,
                "success_rate": 0.99
            }
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/products", json=seller_payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            product_id = response.json()['product_id']
            print(f"\n--- 2. 模拟买家 AI 查询商品 ---")
            
            # 买家查询
            list_response = requests.get(f"{BASE_URL}/api/v1/products")
            print(f"Products List: {json.dumps(list_response.json(), indent=2)}")
            
            print("\n--- 3. 验证合同哈希生成 ---")
            # 检查数据库中是否生成了 contract_hash
            # (此处省略直接查库步骤，通过 API 返回观察)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_micro_transaction_flow()
