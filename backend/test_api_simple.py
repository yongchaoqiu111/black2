import requests
import json
import hashlib
import aiosqlite
import asyncio

BASE_URL = "http://localhost:3000"
DB_PATH = "black2.db"

async def setup_test_user():
    """直接在数据库中创建一个已激活的测试卖家"""
    seller_address = "TTestSellerAI123456789"

def test_micro_transaction_flow(seller_address):
    print("\n--- 1. 模拟卖家 AI 发布微交易商品 ---")
    
    # 准备一个虚拟的交付物哈希
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
            "metrics": {"latency_ms": 150, "success_rate": 0.99}
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/products", json=seller_payload)
    product_id = response.json().get('product_id')
    print(f"Product ID: {product_id}")

    print("\n--- 2. 模拟买家 AI 下单购买 ---")
    buyer_address = "TBuyerAI987654321"
    asyncio.run(setup_test_user(buyer_address))
    
    # 获取商品详情以拿到 contract_hash
    product_res = requests.get(f"{BASE_URL}/api/v1/products/{product_id}")
    if product_res.status_code != 200:
        print(f"Error fetching product: {product_res.text}")
        return
    
    data = product_res.json()
    # 适配后端返回格式：{"product": {...}}
    product_info = data.get('product', data)
    contract_hash = product_info.get('contract_hash')
    if not contract_hash:
        print("Error: Product has no contract_hash")
        return

    order_payload = {
        "from_address": buyer_address,
        "to_address": seller_address,
        "amount": 0.001,
        "currency": "TRX",
        "contract_hash": contract_hash,
        "file_hash": delivery_hash,
        "referrer_address": None
    }
    
    try:
        order_res = requests.post(f"{BASE_URL}/api/v1/transactions", json=order_payload)
        print(f"Order Status: {order_res.status_code}")
        if order_res.status_code != 200:
            print(f"Order Error: {order_res.text}")
            return
            
        tx_id = order_res.json().get('tx_id')
        print(f"Transaction ID: {tx_id}")
    except Exception as e:
        print(f"Order Exception: {e}")
        return

    print("\n--- 3. 模拟卖家 AI 发货 (更新交付物哈希) ---")
    # 实际场景中卖家会调用 update_product_delivery 或类似接口
    # 这里我们假设卖家已经更新了，直接进入仲裁环节

    print("\n--- 4. 模拟买家 AI 发起仲裁 (哈希不匹配-自动退款) ---")
    arb_payload = {
        "reason": "Delivery hash mismatch! The code provided is different from the contract.",
        "evidence_hash": "fake_evidence_hash"
    }
    arb_res = requests.post(f"{BASE_URL}/api/v1/transactions/{tx_id}/dispute", json=arb_payload)
    print(f"Arbitration Status: {arb_res.status_code}")
    if arb_res.status_code == 200:
        print(f"Response: {json.dumps(arb_res.json(), indent=2)}")
    else:
        print(f"Error: {arb_res.text}")

    print("\n--- 5. 模拟买家 AI 恶意退款 (哈希匹配-判定败诉) ---")
    # 准备一个哈希完全匹配的订单
    order_payload_match = order_payload.copy()
    order_payload_match['file_hash'] = contract_hash # 故意让 file_hash 等于 contract_hash
    
    order_res_match = requests.post(f"{BASE_URL}/api/v1/transactions", json=order_payload_match)
    tx_id_match = order_res_match.json().get('tx_id')
    print(f"Matched Transaction ID: {tx_id_match}")
    
    arb_res_2 = requests.post(f"{BASE_URL}/api/v1/transactions/{tx_id_match}/dispute", json={"reason": "Malicious refund attempt"})
    print(f"Malicious Dispute Status: {arb_res_2.status_code}")
    print(f"Response: {json.dumps(arb_res_2.json(), indent=2)}")

    print("\n--- 6. 模拟批量微交易与异步锚定 ---")
    print("Creating 5 micro-transactions rapidly...")
    for i in range(5):
        requests.post(f"{BASE_URL}/api/v1/transactions", json=order_payload)
    print("Batch transactions created. Check server logs for 'Anchor queued' messages.")

async def setup_test_user(address):
    """直接在数据库中创建一个已激活的测试用户并充值"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (email, password_hash, address, is_verified) VALUES (?, ?, ?, 1)",
            (f"user_{address}@ai.com", "hash", address)
        )
        # 为 AI 钱包充值，确保能买得起东西
        await db.execute(
            "INSERT OR REPLACE INTO ai_wallets (address, balance) VALUES (?, ?)",
            (address, 100.0)
        )
        await db.commit()

if __name__ == "__main__":
    # 1. 运行测试
    test_micro_transaction_flow("TTestSellerAI123456789")
