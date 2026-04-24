# Black2 Data Structure & Privacy Context

## 1. Reputation Data Model
**File:** `b2p-repo.json` (Stored in Git)
```json
{
  "agent_id": "0x...",
  "macro_metrics": {
    "reputation_score": 850,
    "friction_index": 0.15,
    "total_volume_usd": 125000.00
  },
  "micro_proofs": [
    {
      "tx_hash": "0x...",
      "evidence_hash": "sha256:..." 
    }
  ]
}
```

## 2. AI Interaction API
**File:** `backend/src/api/ai_routes.py`
```python
@app.route('/api/v1/reputation/{address}')
def get_reputation(address):
    """
    外部 AI 查询信誉的接口
    目前只返回脱敏后的宏观指标
    """
    return {
        "score": 850,
        "risk_level": "LOW"
    }
```

## 3. Privacy Challenge
*   **Issue:** X402 transactions are public on-chain.
*   **Requirement:** We need a way to link an on-chain X402 payment to a B2P reputation update without revealing that "AI_A (0x123)" is actually "Company_X".
