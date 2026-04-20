import unittest
from arbitrator import Arbitrator

class TestArbitrator(unittest.TestCase):
    def setUp(self):
        self.arbitrator = Arbitrator()
    
    def test_seller_wins_when_hash_matches(self):
        """测试哈希匹配的场景 - 卖家胜"""
        result = self.arbitrator.arbitrate(
            tx_id="tx_123",
            contract_hash="abc123",
            file_hash="abc123"
        )
        self.assertEqual(result["verdict"], "seller_wins")
        self.assertEqual(result["reason"], "Contract hash matches delivered file")
        self.assertEqual(result["tx_id"], "tx_123")
    
    def test_buyer_wins_when_hash_mismatches(self):
        """测试哈希不匹配的场景 - 买家胜"""
        result = self.arbitrator.arbitrate(
            tx_id="tx_123",
            contract_hash="abc123",
            file_hash="def456"
        )
        self.assertEqual(result["verdict"], "buyer_wins")
        self.assertEqual(result["reason"], "Delivered file hash does not match contract hash")
        self.assertEqual(result["tx_id"], "tx_123")
    
    def test_buyer_wins_when_no_file(self):
        """测试未交付的场景 - 买家胜"""
        result = self.arbitrator.arbitrate(
            tx_id="tx_123",
            contract_hash="abc123",
            file_hash=""
        )
        self.assertEqual(result["verdict"], "buyer_wins")
        self.assertEqual(result["reason"], "Seller did not deliver the file")
        self.assertEqual(result["tx_id"], "tx_123")

if __name__ == "__main__":
    unittest.main()
