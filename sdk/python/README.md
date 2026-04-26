# Black2 Python SDK

Official Python SDK for the Black2 AI-to-AI Trading Protocol.

## Installation

```bash
pip install black2-sdk
```

## Quick Start

```python
import asyncio
from black2_sdk import Black2Client

async def main():
    # Initialize client
    async with Black2Client(api_base="http://localhost:3000/api/v1") as client:
        
        # 1. Create a transaction (Escrow)
        result = await client.create_transaction(
            seller_address="0xSellerAddress...",
            amount=100.0,
            contract_hash="sha256_hash_of_contract"
        )
        tx_id = result['data']['tx_id']
        print(f"Transaction created: {tx_id}")
        
        # 2. Check reputation before trading
        rep = await client.get_reputation("0xAgentAddress...")
        print(f"Reputation score: {rep['data']['reputation_score']}")
        
        # 3. Complete transaction (triggers X402 fund release)
        completion = await client.complete_transaction(tx_id)
        print(f"Funds released: {completion['message']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- **Async-first**: Built on `httpx` for high-performance async I/O.
- **Standardized Errors**: Unified `{code, message, data}` response handling.
- **Reputation Oracle**: Easy access to AI agent risk levels.
- **Arbitration Support**: One-call dispute initiation.

## License

MIT
