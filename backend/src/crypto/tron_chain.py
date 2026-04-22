"""
Tron Chain Service - Real on-chain wallet operations
"""

from tronpy import Tron
from tronpy.keys import PrivateKey
import os
from typing import Dict, Optional, List

class TronChainService:
    """波场链上服务 - 处理真实 USDT-TRC20 交易"""
    
    def __init__(self, network: str = "mainnet"):
        """
        初始化波场服务
        
        Args:
            network: "mainnet" 或 "testnet"
        """
        # 初始化 Tron 客户端
        if network == "testnet":
            self.client = Tron(network='testnet')
        else:
            self.client = Tron(network='mainnet')
        
        # 加载平台母钱包
        private_key_hex = os.getenv("PLATFORM_WALLET_PRIVATE_KEY")
        self.platform_address = os.getenv("PLATFORM_WALLET_ADDRESS")
        
        if not private_key_hex or not self.platform_address:
            raise ValueError("PLATFORM_WALLET_PRIVATE_KEY and PLATFORM_WALLET_ADDRESS must be set in .env")
        
        self.platform_private_key = PrivateKey.fromhex(private_key_hex)
        self.client.default_private_key = self.platform_private_key
        
        # USDT-TRC20 合约地址（波场主网）
        self.usdt_contract_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        self.usdt_contract = None  # 延迟初始化
        
        print(f"[TronChain] Platform wallet: {self.platform_address}")
        print(f"[TronChain] USDT contract: {self.usdt_contract_address}")
        print(f"[TronChain] Contract lazy-loaded (rate limit safe)")
    
    def _get_usdt_contract(self):
        """Lazy load USDT contract (avoid rate limits)"""
        if self.usdt_contract is None:
            import time
            time.sleep(1)  # Wait to avoid rate limit
            self.usdt_contract = self.client.get_contract(self.usdt_contract_address)
        return self.usdt_contract
    
    def generate_sub_wallet(self) -> Dict[str, str]:
        """
        生成子钱包地址
        
        Returns:
            {"address": "T...", "private_key": "hex"}
        """
        import secrets
        
        # 生成随机私钥
        random_bytes = secrets.token_bytes(32)
        private_key = PrivateKey.fromhex(random_bytes.hex())
        
        # 获取地址
        address = private_key.public_key.to_base58check_address()
        
        return {
            "address": address,
            "private_key": private_key.hex()
        }
    
    def get_balance(self, address: str) -> float:
        """
        查询 USDT-TRC20 余额
        """
        try:
            contract = self._get_usdt_contract()
            balance = contract.functions.balanceOf(address)
            return float(balance) / 1_000_000
        except Exception as e:
            print(f"[TronChain] Get balance error: {e}")
            return 0.0
    
    def get_trx_balance(self, address: str) -> float:
        """
        查询 TRX 余额（用于 Gas）
        """
        try:
            balance = self.client.get_account_balance(address)
            return float(balance) / 1_000_000
        except Exception as e:
            print(f"[TronChain] Get TRX balance error: {e}")
            return 0.0
    
    def transfer_usdt(self, to_address: str, amount: float) -> Dict[str, str]:
        """
        发送 USDT-TRC20
        
        Args:
            to_address: 接收地址
            amount: 金额
            
        Returns:
            {"tx_id": "...", "status": "success"}
        """
        try:
            # USDT 精度转换
            amount_raw = int(amount * 1_000_000)
            
            # 构建转账交易
            txn = (
                self.usdt_contract.functions.transfer(to_address, amount_raw)
                .with_owner(self.platform_address)
                .fee_limit(5_000_000)  # 5 TRX Gas 限制
                .build()
                .sign(self.platform_private_key)
            )
            
            # 广播交易
            result = txn.broadcast()
            
            return {
                "tx_id": result["txid"],
                "status": "success",
                "message": "Transaction broadcasted"
            }
        except Exception as e:
            print(f"[TronChain] Transfer error: {e}")
            raise ValueError(f"Transfer failed: {str(e)}")
    
    def monitor_deposit(self, address: str, min_amount: float = 0.01) -> List[Dict]:
        """
        查询地址最近的 USDT 入账记录
        
        Args:
            address: 要查询的地址
            min_amount: 最小金额过滤
            
        Returns:
            交易记录列表
        """
        try:
            # 获取地址的 USDT 转账事件
            events = self.client.get_contract_events(
                self.usdt_contract_address,
                event_name="Transfer",
                size=20
            )
            
            deposits = []
            for event in events:
                # 解析 Transfer 事件
                if event.get('result', {}).get('to') == address:
                    from_addr = event.get('result', {}).get('from', '')
                    amount_raw = event.get('result', {}).get('value', 0)
                    amount = float(amount_raw) / 1_000_000
                    
                    if amount >= min_amount:
                        deposits.append({
                            "tx_id": event.get('transaction_id', ''),
                            "from": from_addr,
                            "to": address,
                            "amount": amount,
                            "timestamp": event.get('block_timestamp', 0)
                        })
            
            return deposits
        except Exception as e:
            print(f"[TronChain] Monitor deposit error: {e}")
            return []
    
    def verify_tx(self, tx_id: str) -> Dict[str, any]:
        """
        验证交易是否上链成功
        
        Args:
            tx_id: 交易哈希
            
        Returns:
            交易信息
        """
        try:
            tx_info = self.client.get_transaction(tx_id)
            
            return {
                "confirmed": tx_info.get('ret', [{}])[0].get('contractRet') == 'SUCCESS',
                "block_number": tx_info.get('blockNumber'),
                "timestamp": tx_info.get('block_timestamp'),
                "energy_usage": tx_info.get('energy_usage', 0),
                "energy_fee": tx_info.get('energy_fee', 0)
            }
        except Exception as e:
            print(f"[TronChain] Verify tx error: {e}")
            return {"confirmed": False, "error": str(e)}
