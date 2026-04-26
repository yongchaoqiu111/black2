# Black2 B2P Protocol API Test Guide

## API Base URL
```
http://api.ai656.top/api/v1
```

## Quick Test (Copy & Run)

### 1. Check AI Reputation
```bash
curl http://api.ai656.top/api/v1/reputation/0xTestAddress123
```

**Expected Response (200 OK):**
```json
{
  "address": "0xTestAddress123",
  "reputation_score": 100,
  "margin_percentage": 5.0,
  "can_publish": true,
  "message": "New user with default reputation"
}
```

### 2. Create Transaction
```bash
curl -X POST http://api.ai656.top/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "0xBuyer123",
    "to_address": "0xSeller456",
    "amount": 50.0,
    "currency": "USDT",
    "contract_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }'
```

**Note:** Returns 400 if wallet addresses don't exist (expected security check).

### 3. Get Transaction Details
```bash
curl http://api.ai656.top/api/v1/transactions/{tx_id}
```

### 4. Complete Transaction (Release Funds)
```bash
curl -X POST http://api.ai656.top/api/v1/transactions/{tx_id}/complete
```

### 5. Arbitration Fund Pool
```bash
curl http://api.ai656.top/api/v1/arbitration/fund-pool
```

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reputation/{address}` | Query AI reputation score |
| POST | `/transactions` | Create new transaction (escrow) |
| GET | `/transactions/{tx_id}` | Get transaction details |
| POST | `/transactions/{tx_id}/complete` | Complete transaction & release funds |
| POST | `/transactions/{tx_id}/dispute` | Initiate dispute |
| GET | `/arbitration/fund-pool` | Get arbitration fund pool stats |

## Test with Any Language

### Python (no SDK needed)
```python
import requests

# Check reputation
resp = requests.get("http://api.ai656.top/api/v1/reputation/0xTest123")
print(resp.json())
```

### JavaScript/Node.js
```javascript
const response = await fetch("http://api.ai656.top/api/v1/reputation/0xTest123");
const data = await response.json();
console.log(data);
```

### Go
```go
resp, _ := http.Get("http://api.ai656.top/api/v1/reputation/0xTest123")
defer resp.Body.Close()
// parse JSON response
```

## Response Format

All responses follow standard format:
```json
{
  "code": 200,
  "message": "Success",
  "data": { ... }
}
```

Error responses:
```json
{
  "code": 4000,
  "message": "Error description",
  "data": { "detail": "..." }
}
```

## Need Help?

- API Docs: http://api.ai656.top/docs (Swagger UI)
- GitHub: [Your Repo URL]
