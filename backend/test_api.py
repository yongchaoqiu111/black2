import requests
import json

# 测试API是否存在
url = "http://localhost:3000/api/v1/admin/deposits/manual"
data = {
    "user_address": "test_address",
    "amount": 100,
    "reason": "测试"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
