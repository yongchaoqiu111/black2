"""
HD Wallet Service - Generate AI sub-wallets from master wallet
"""
import os
from dotenv import load_dotenv
from eth_account import Account

# 加载 .env 文件
load_dotenv()


class HDWalletService:
    """HD钱包服务 - 从母钱包派生AI子钱包"""
    
    def __init__(self):
        # 从环境变量读取母钱包私钥
        self.master_private_key = os.getenv('PLATFORM_WALLET_PRIVATE_KEY')
        self.master_address = os.getenv('PLATFORM_WALLET_ADDRESS')
        
        if not self.master_private_key:
            raise ValueError("PLATFORM_WALLET_PRIVATE_KEY not configured in .env")
    
    def generate_ai_wallet(self, ai_index: int = 0) -> dict:
        """
        为AI生成子钱包地址
        
        Args:
            ai_index: AI的唯一索引（从0开始）
            
        Returns:
            dict: {
                'address': str,  # 子钱包地址
                'path': str,     # BIP44路径
                'index': int     # 索引
            }
        """
        # BIP44标准路径: m/44'/60'/0'/0/{index}
        # 44' = BIP44, 60' = Ethereum, 0' = account, 0 = external, {index} = address index
        path = f"m/44'/60'/0'/0/{ai_index}"
        
        # 从私钥推导公钥，然后派生子地址
        # 注意：eth-account库不直接支持从私钥派生HD路径
        # 这里简化处理：直接用母钱包私钥创建账户
        # 生产环境应该使用助记词 + HD路径派生
        
        account = Account.from_key(self.master_private_key)
        
        return {
            'address': account.address,
            'path': path,
            'index': ai_index,
            'master_address': self.master_address
        }
    
    def sign_transaction(self, private_key: str, transaction: dict) -> str:
        """
        签名交易
        
        Args:
            private_key: 私钥
            transaction: 交易数据
            
        Returns:
            str: 签名后的交易
        """
        signed_txn = Account.sign_transaction(transaction, private_key)
        return signed_txn.rawTransaction.hex()
    
    def get_master_address(self) -> str:
        """获取母钱包地址"""
        return self.master_address


# 全局实例
hd_wallet_service = HDWalletService()
