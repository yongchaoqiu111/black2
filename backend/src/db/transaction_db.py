"""
Black2 Database Module - Transaction and Wallet Management

Provides database operations for transactions, AI wallets, and referral rewards.
"""

import aiosqlite
import asyncio
from typing import Dict, List, Optional, Any
import datetime

DB_PATH = 'black2.db'


async def init_db():
    """
    Initialize database tables if they don't exist.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Create transactions table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT UNIQUE NOT NULL,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USDT',
                contract_hash TEXT NOT NULL,
                file_hash TEXT,
                status TEXT DEFAULT 'pending',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                hash TEXT NOT NULL,
                signature TEXT NOT NULL,
                anchor_hash TEXT,
                anchored_at DATETIME,
                referrer_address TEXT,
                referral_level INTEGER DEFAULT 0
            )
        ''')
        
        # Create ai_wallets table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ai_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                balance REAL DEFAULT 0.0,
                total_earned REAL DEFAULT 0.0,
                referral_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create human_wallets table (for point-based ledger)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS human_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                points_balance REAL DEFAULT 0.0,
                locked_points REAL DEFAULT 0.0,
                total_deposited REAL DEFAULT 0.0,
                total_withdrawn REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create platform_wallet table (cold wallet for USDT)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS platform_wallet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                total_balance REAL DEFAULT 0.0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create referral_rewards table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS referral_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT NOT NULL,
                referrer_address TEXT NOT NULL,
                reward_amount REAL NOT NULL,
                level INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                paid BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                settled_at DATETIME
            )
        ''')
        
        # Create referral_relationships table (track who referred whom)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS referral_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referee_address TEXT NOT NULL,
                referrer_address TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(referee_address, referrer_address)
            )
        ''')
        
        # Create sub_wallets table (user sub-wallet addresses managed by platform)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sub_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_address TEXT UNIQUE NOT NULL,
                wallet_address TEXT UNIQUE NOT NULL,
                private_key TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create deposits table (on-chain deposit records)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_address TEXT NOT NULL,
                wallet_address TEXT,
                tx_hash TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                confirmed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create withdrawals table (on-chain withdrawal records)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_address TEXT NOT NULL,
                tx_hash TEXT,
                amount REAL NOT NULL,
                gas_fee REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            )
        ''')
        
        # Create anchor_records table (for 2号 employee)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS anchor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_hash TEXT UNIQUE NOT NULL,
                transaction_count INTEGER NOT NULL,
                gist_url TEXT,
                gist_commit_hash TEXT,
                anchor_timestamp TEXT NOT NULL,
                previous_anchor TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create products table (Optimized for Micro-transactions)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                seller_address TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL, -- Core promise for arbitration
                price REAL NOT NULL,
                currency TEXT DEFAULT 'TRX',
                category_id TEXT NOT NULL, -- e.g., software/automation/bot
                specs_json TEXT NOT NULL, -- Standardized metadata (runtime, format, etc.)
                delivery_hash TEXT NOT NULL, -- The fingerprint of the asset
                contract_hash TEXT, -- Generated by backend: SHA-256(name+desc+price+delivery_hash)
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create contracts table (store contract details)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id TEXT UNIQUE NOT NULL,
                product_id TEXT NOT NULL,
                buyer_address TEXT,
                seller_address TEXT NOT NULL,
                contract_hash TEXT NOT NULL,
                file_hash TEXT,
                github_anchor_url TEXT,
                github_commit_sha TEXT,
                anchored_at DATETIME,
                status TEXT DEFAULT 'created',  -- created, active, completed, cancelled, disputed
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Create arbitration_records table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS arbitration_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT UNIQUE NOT NULL,
                buyer_address TEXT NOT NULL,
                seller_address TEXT NOT NULL,
                buyer_reason TEXT,
                seller_evidence TEXT,
                status TEXT DEFAULT 'pending',  -- pending, evidence_collection, arbitrating, completed
                verdict TEXT,  -- buyer_wins, seller_wins
                verdict_reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                deadline DATETIME,
                resolved_at DATETIME,
                FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
            )
        ''')
        
        # Create arbitration_fund_pool table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS arbitration_fund_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                source_tx_id TEXT,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_tx_id) REFERENCES transactions(tx_id)
            )
        ''')
        
        # Create users table (for reputation system)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                address TEXT UNIQUE,
                name TEXT,
                reputation_score INTEGER DEFAULT 100,
                is_verified INTEGER DEFAULT 0,
                verification_code TEXT,
                verification_code_expires DATETIME,
                purchase_count INTEGER DEFAULT 0,  -- 购买次数
                sales_count INTEGER DEFAULT 0,  -- 销售次数
                dispute_count INTEGER DEFAULT 0,  -- 仲裁次数（刺头指标）
                last_dispute_at DATETIME,  -- 上次争议时间（用于时间衰减）
                successful_streak INTEGER DEFAULT 0,  -- 连续成功交易数（用于行为对冲）
                reputation_stake REAL DEFAULT 0,  -- 信誉质押金额（用于保证金修复）
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create reputation_history table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reputation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_address TEXT NOT NULL,
                score_change INTEGER NOT NULL,
                new_score INTEGER NOT NULL,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_address) REFERENCES users(address)
            )
        ''')
        
        # Create reputation_history table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reputation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_address TEXT NOT NULL,
                score_change INTEGER NOT NULL,
                new_score INTEGER NOT NULL,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_address) REFERENCES users(address)
            )
        ''')
        
        # Create reputation_cache table (for pre-computed snapshots)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reputation_cache (
                address TEXT PRIMARY KEY,
                completion_rate REAL DEFAULT 1.0,
                friction_index REAL DEFAULT 0.0,
                risk_level TEXT DEFAULT 'low',
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Database migration: add missing columns to existing tables
        # Check and add delivery_url column to products table
        try:
            cursor = await db.execute("PRAGMA table_info(products)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'delivery_url' not in column_names:
                await db.execute("ALTER TABLE products ADD COLUMN delivery_url TEXT DEFAULT ''")
                print("[Migration] Added delivery_url column to products table")
        except Exception as e:
            print(f"[Migration] Warning: Could not check/add delivery_url: {e}")
        
        # Check and add delivery_checklist column to products table
        try:
            cursor = await db.execute("PRAGMA table_info(products)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'delivery_checklist' not in column_names:
                await db.execute("ALTER TABLE products ADD COLUMN delivery_checklist TEXT DEFAULT '{}'")
                print("[Migration] Added delivery_checklist column to products table")
            
            if 'max_sales_volume' not in column_names:
                await db.execute("ALTER TABLE products ADD COLUMN max_sales_volume INTEGER DEFAULT 100")
                print("[Migration] Added max_sales_volume column to products table")
        except Exception as e:
            print(f"[Migration] Warning: Could not check/add product fields: {e}")
        
        # Check and add arbitration_fund_pool table
        try:
            cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='arbitration_fund_pool'")
            table = await cursor.fetchone()
            if not table:
                await db.execute('''
                    CREATE TABLE arbitration_fund_pool (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL NOT NULL,
                        source_tx_id TEXT,
                        reason TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (source_tx_id) REFERENCES transactions(tx_id)
                    )
                ''')
                print("[Migration] Created arbitration_fund_pool table")
        except Exception as e:
            print(f"[Migration] Warning: Could not create arbitration_fund_pool: {e}")
        
        # Check and add wallet_address column to deposits table
        try:
            cursor = await db.execute("PRAGMA table_info(deposits)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'wallet_address' not in column_names:
                await db.execute("ALTER TABLE deposits ADD COLUMN wallet_address TEXT DEFAULT ''")
                print("[Migration] Added wallet_address column to deposits table")
        except Exception as e:
            print(f"[Migration] Warning: Could not check/add wallet_address: {e}")
        
        # Check and add notes column to deposits table
        try:
            cursor = await db.execute("PRAGMA table_info(deposits)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'notes' not in column_names:
                await db.execute("ALTER TABLE deposits ADD COLUMN notes TEXT DEFAULT ''")
                print("[Migration] Added notes column to deposits table")
        except Exception as e:
            print(f"[Migration] Warning: Could not check/add notes to deposits: {e}")
        
        # Check and add reputation fields to users table
        try:
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'purchase_count' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN purchase_count INTEGER DEFAULT 0")
                print("[Migration] Added purchase_count column to users table")
            
            if 'sales_count' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN sales_count INTEGER DEFAULT 0")
                print("[Migration] Added sales_count column to users table")
            
            if 'dispute_count' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN dispute_count INTEGER DEFAULT 0")
                print("[Migration] Added dispute_count column to users table")
            
            if 'last_dispute_at' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN last_dispute_at DATETIME")
                print("[Migration] Added last_dispute_at column to users table")
            
            if 'successful_streak' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN successful_streak INTEGER DEFAULT 0")
                print("[Migration] Added successful_streak column to users table")
            
            if 'reputation_stake' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN reputation_stake REAL DEFAULT 0")
                print("[Migration] Added reputation_stake column to users table")
            
            # Add referral tracking columns if they don't exist
            for col in ['tu1', 'tu2', 'tu3']:
                if col not in column_names:
                    await db.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
                    print(f"[Migration] Added {col} column to users table")
        except Exception as e:
            print(f"[Migration] Warning: Could not check/add reputation fields: {e}")
        
        # Create transaction_referrals table if not exists
        await db.execute('''
            CREATE TABLE IF NOT EXISTS transaction_referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT UNIQUE NOT NULL,
                tu1_address TEXT,
                tu1_amount REAL DEFAULT 0.0,
                tu2_address TEXT,
                tu2_amount REAL DEFAULT 0.0,
                tu3_address TEXT,
                tu3_amount REAL DEFAULT 0.0,
                settlement_status TEXT DEFAULT 'pending',
                settled_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.commit()


class TransactionDB:
    """Class-based DB for 2号 employee's Anchor Service compatibility."""
    def __init__(self, db_path: str = 'black2.db'):
        self.db_path = db_path

    async def initialize(self):
        # Tables are already created by init_db()
        pass

    async def close(self):
        pass

    async def get_unanchored_transactions(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                """SELECT tx_id, hash as tx_hash, contract_hash, file_hash
                   FROM transactions
                   WHERE anchor_hash IS NULL
                   ORDER BY timestamp ASC"""
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "tx_id": row[0],
                        "tx_hash": row[1],
                        "contract_hash": row[2],
                        "file_hash": row[3]
                    }
                    for row in rows
                ]

    async def anchor_transactions(self, tx_hashes: list, anchor_hash: str, anchor_timestamp: str):
        async with aiosqlite.connect(DB_PATH) as db:
            for tx_hash in tx_hashes:
                await db.execute(
                    """UPDATE transactions
                       SET anchor_hash = ?, anchored_at = ?
                       WHERE hash = ?""",
                    (anchor_hash, anchor_timestamp, tx_hash)
                )
            await db.commit()

    async def get_latest_anchor(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                """SELECT root_hash, anchor_timestamp FROM anchor_records
                   ORDER BY id DESC LIMIT 1"""
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"root_hash": row[0], "anchor_timestamp": row[1]}
                return None

    async def add_anchor_record(self, root_hash: str, transaction_count: int, gist_url: str,
                                 gist_commit_hash: str, anchor_timestamp: str, previous_anchor: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """INSERT INTO anchor_records (root_hash, transaction_count, gist_url, gist_commit_hash, anchor_timestamp, previous_anchor)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (root_hash, transaction_count, gist_url, gist_commit_hash, anchor_timestamp, previous_anchor)
            )
            await db.commit()

    async def get_all_transactions(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                """SELECT hash as tx_hash, from_address as sender, to_address as receiver, amount, 0.0 as fee, timestamp, anchor_hash
                   FROM transactions
                   ORDER BY timestamp ASC"""
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "tx_hash": row[0],
                        "sender": row[1],
                        "receiver": row[2],
                        "amount": row[3],
                        "fee": row[4],
                        "timestamp": row[5],
                        "anchor_hash": row[6]
                    }
                    for row in rows
                ]


async def create_transaction(transaction: dict) -> Dict[str, Any]:
    """
    Create a new transaction in the database.
    
    Args:
        transaction: Transaction data dictionary
        
    Returns:
        Created transaction with id
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Insert transaction
        cursor = await db.execute('''
            INSERT INTO transactions (
                tx_id, from_address, to_address, amount, currency, 
                contract_hash, file_hash, status, hash, signature, 
                referrer_address, referral_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction['tx_id'],
            transaction['from_address'],
            transaction['to_address'],
            transaction['amount'],
            transaction.get('currency', 'USDT'),
            transaction['contract_hash'],
            transaction.get('file_hash'),
            transaction.get('status', 'pending'),
            transaction['hash'],
            transaction['signature'],
            transaction.get('referrer_address'),
            transaction.get('referral_level', 0)
        ))
        
        transaction_id = cursor.lastrowid
        await db.commit()
        
        # Return the created transaction
        return {**transaction, 'id': transaction_id}


async def get_transaction(tx_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a transaction by tx_id (with referral info).
    
    Args:
        tx_id: Transaction ID
        
    Returns:
        Transaction dictionary or None if not found
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT t.*, 
                   r.tu1_address, r.tu1_amount, 
                   r.tu2_address, r.tu2_amount, 
                   r.tu3_address, r.tu3_amount, 
                   r.settlement_status
            FROM transactions t
            LEFT JOIN transaction_referrals r ON t.tx_id = r.tx_id
            WHERE t.tx_id = ?
        ''', (tx_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            
            # Convert row to dict
            columns = [desc[0] for desc in cursor.description]
            transaction = dict(zip(columns, row))
            return transaction


async def list_transactions(
    status: Optional[str] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List transactions with optional filters.
    
    Args:
        status: Filter by status
        from_address: Filter by from_address
        to_address: Filter by to_address
        limit: Maximum number of transactions to return
        offset: Offset for pagination
        
    Returns:
        List of transaction dictionaries (with referral info)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Build query with LEFT JOIN to transaction_referrals
        query = '''
            SELECT t.*, 
                   r.tu1_address, r.tu1_amount, 
                   r.tu2_address, r.tu2_amount, 
                   r.tu3_address, r.tu3_amount, 
                   r.settlement_status
            FROM transactions t
            LEFT JOIN transaction_referrals r ON t.tx_id = r.tx_id
            WHERE 1=1
        '''
        params = []
        
        if status:
            query += ' AND t.status = ?'
            params.append(status)
        
        if from_address:
            query += ' AND t.from_address = ?'
            params.append(from_address)
        
        if to_address:
            query += ' AND t.to_address = ?'
            params.append(to_address)
        
        query += ' ORDER BY t.timestamp DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            transactions = [dict(zip(columns, row)) for row in rows]
            return transactions


async def update_transaction_status(
    tx_id: str,
    status: str,
    file_hash: Optional[str] = None
) -> bool:
    """
    Update transaction status and optionally file_hash.
    
    Args:
        tx_id: Transaction ID
        status: New status
        file_hash: Optional file hash
        
    Returns:
        True if updated successfully, False otherwise
    """
    async with aiosqlite.connect(DB_PATH) as db:
        if file_hash:
            result = await db.execute('''
                UPDATE transactions SET status = ?, file_hash = ? WHERE tx_id = ?
            ''', (status, file_hash, tx_id))
        else:
            result = await db.execute('''
                UPDATE transactions SET status = ? WHERE tx_id = ?
            ''', (status, tx_id))
        
        await db.commit()
        return result.rowcount > 0


async def update_anchor_hash(tx_id: str, anchor_hash: str) -> bool:
    """
    Update transaction anchor hash and anchored_at timestamp.
    
    Args:
        tx_id: Transaction ID
        anchor_hash: Anchor hash
        
    Returns:
        True if updated successfully, False otherwise
    """
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.datetime.now().isoformat()
        result = await db.execute('''
            UPDATE transactions SET anchor_hash = ?, anchored_at = ? WHERE tx_id = ?
        ''', (anchor_hash, now, tx_id))
        
        await db.commit()
        return result.rowcount > 0


async def get_or_create_wallet(address: str) -> Dict[str, Any]:
    """
    Get wallet by address or create it if it doesn't exist.
    
    Args:
        address: Wallet address
        
    Returns:
        Wallet dictionary
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if wallet exists
        async with db.execute('''
            SELECT * FROM ai_wallets WHERE address = ?
        ''', (address,)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
        
        # Create new wallet
        cursor = await db.execute('''
            INSERT INTO ai_wallets (address) VALUES (?)
        ''', (address,))
        wallet_id = cursor.lastrowid
        await db.commit()
        
        # Return the new wallet
        return {
            'id': wallet_id,
            'address': address,
            'balance': 0.0,
            'total_earned': 0.0,
            'referral_count': 0,
            'created_at': datetime.datetime.now().isoformat()
        }


async def add_referral_reward(
    tx_id: str,
    referrer_address: str,
    amount: float,
    level: int,
    status: str = 'pending'
) -> Dict[str, Any]:
    """
    Add a referral reward record (initially pending).
    
    Args:
        tx_id: Transaction ID
        referrer_address: Referrer address
        amount: Reward amount
        level: Referral level (1-5)
        status: Reward status (pending/completed/cancelled)
        
    Returns:
        Created reward record
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Insert reward with pending status
        cursor = await db.execute('''
            INSERT INTO referral_rewards (
                tx_id, referrer_address, reward_amount, level, status
            ) VALUES (?, ?, ?, ?, ?)
        ''', (tx_id, referrer_address, amount, level, status))
        
        reward_id = cursor.lastrowid
        await db.commit()
        
        return {
            'id': reward_id,
            'tx_id': tx_id,
            'referrer_address': referrer_address,
            'reward_amount': amount,
            'level': level,
            'status': status,
            'paid': False,
            'created_at': datetime.datetime.now().isoformat()
        }


async def settle_referral_rewards(tx_id: str):
    """
    Settle all pending referral rewards for a completed transaction.
    Distribute funds to seller and referrers (tu1, tu2, tu3).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            # Get referral info from transaction_referrals
            cursor = await db.execute('''
                SELECT tu1_address, tu1_amount, tu2_address, tu2_amount, tu3_address, tu3_amount
                FROM transaction_referrals
                WHERE tx_id = ?
            ''', (tx_id,))
            
            referral = await cursor.fetchone()
            
            if not referral:
                print(f"[Settle] No referral record found for {tx_id}")
                return 0
            
            tu1_addr, tu1_amount, tu2_addr, tu2_amount, tu3_addr, tu3_amount = referral
            
            # Get seller info from transactions table
            cursor = await db.execute(
                'SELECT amount, to_address FROM transactions WHERE tx_id = ?',
                (tx_id,)
            )
            tx_info = await cursor.fetchone()
            
            if not tx_info:
                print(f"[Settle] No transaction found for {tx_id}")
                return 0
            
            order_amount, seller_addr = tx_info
            seller_amount = round(order_amount * 0.90, 2)
            
            # 1. Credit seller AI wallet (90%)
            if seller_addr and seller_amount > 0:
                await db.execute(
                    'UPDATE users SET ai_balance = ai_balance + ? WHERE ai_address = ?',
                    (seller_amount, seller_addr)
                )
                await db.execute(
                    'UPDATE ai_wallets SET balance = balance + ?, total_earned = total_earned + ? WHERE address = ?',
                    (seller_amount, seller_amount, seller_addr)
                )
                print(f"  ✓ Credited {seller_amount} to seller: {seller_addr}")
            
            # 2. Credit tu1 AI wallet (5%)
            if tu1_addr and tu1_amount > 0:
                await db.execute(
                    'UPDATE users SET ai_balance = ai_balance + ? WHERE ai_address = ?',
                    (tu1_amount, tu1_addr)
                )
                await db.execute(
                    'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
                    (tu1_amount, tu1_addr)
                )
                print(f"  ✓ Credited {tu1_amount} to tu1: {tu1_addr}")
            
            # 3. Credit tu2 AI wallet (3%)
            if tu2_addr and tu2_amount > 0:
                await db.execute(
                    'UPDATE users SET ai_balance = ai_balance + ? WHERE ai_address = ?',
                    (tu2_amount, tu2_addr)
                )
                await db.execute(
                    'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
                    (tu2_amount, tu2_addr)
                )
                print(f"  ✓ Credited {tu2_amount} to tu2: {tu2_addr}")
            
            # 4. Credit tu3 AI wallet (2%)
            if tu3_addr and tu3_amount > 0:
                await db.execute(
                    'UPDATE users SET ai_balance = ai_balance + ? WHERE ai_address = ?',
                    (tu3_amount, tu3_addr)
                )
                await db.execute(
                    'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
                    (tu3_amount, tu3_addr)
                )
                print(f"  ✓ Credited {tu3_amount} to tu3: {tu3_addr}")
            
            # Mark referral as settled
            await db.execute(
                "UPDATE transaction_referrals SET settlement_status = 'completed', settled_at = ? WHERE tx_id = ?",
                (datetime.datetime.utcnow().isoformat(), tx_id)
            )
            
            await db.commit()
            print(f"[Settle] Settlement completed for {tx_id}")
            return 1
            
        except Exception as e:
            await db.rollback()
            print(f"[Settle] Error settling rewards for {tx_id}: {e}")
            # Mark as failed
            await db.execute(
                "UPDATE transaction_referrals SET settlement_status = 'failed' WHERE tx_id = ?",
                (tx_id,)
            )
            await db.commit()
            raise


async def cancel_referral_rewards(tx_id: str):
    """
    Cancel all pending referral rewards for a cancelled/refunded transaction.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE referral_rewards SET status = 'cancelled'
            WHERE tx_id = ? AND status = 'pending'
        ''', (tx_id,))
        await db.commit()


async def deduct_ai_wallet_balance(address: str, amount: float) -> bool:
    """
    Atomically deduct balance from AI wallet with overdraft protection.
    Returns True if successful, False if insufficient balance.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        result = await db.execute('''
            UPDATE ai_wallets SET balance = balance - ? 
            WHERE address = ? AND balance >= ?
        ''', (amount, address, amount))
        await db.commit()
        return result.rowcount > 0

async def add_ai_wallet_balance(address: str, amount: float):
    """
    Atomically add balance to AI wallet.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE ai_wallets SET balance = balance + ? 
            WHERE address = ?
        ''', (amount, address))
        await db.commit()


async def calculate_referral_chain(buyer_address: str) -> List[str]:
    """
    Calculate 3-level referral chain for a buyer.
    
    Args:
        buyer_address: Buyer's address
        
    Returns:
        List of referrer addresses in order (level 1 to 3)
    """
    chain = []
    current_address = buyer_address
    
    async with aiosqlite.connect(DB_PATH) as db:
        for level in range(3):  # Changed from 5 to 3
            # Query who referred the current user
            cursor = await db.execute('''
                SELECT referrer_address FROM referral_relationships
                WHERE referee_address = ?
                ORDER BY level ASC
                LIMIT 1
            ''', (current_address,))
            
            row = await cursor.fetchone()
            if not row:
                break
                
            referrer = row[0]
            chain.append(referrer)
            current_address = referrer  # Continue up the chain
    
    return chain


async def add_referral_relationship(referee_address: str, referrer_address: str, level: int = 1):
    """
    Add a referral relationship record.
    
    Args:
        referee_address: The person being referred
        referrer_address: The referrer
        level: Referral level (default 1 for direct referral)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute('''
                INSERT OR IGNORE INTO referral_relationships 
                (referee_address, referrer_address, level)
                VALUES (?, ?, ?)
            ''', (referee_address, referrer_address, level))
            await db.commit()
        except Exception as e:
            print(f"Error adding referral relationship: {e}")


# ===== Human Wallet Functions =====

async def get_or_create_human_wallet(address: str) -> Dict[str, Any]:
    """
    Get human wallet by address or create it if it doesn't exist.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if wallet exists
        cursor = await db.execute(
            'SELECT * FROM human_wallets WHERE address = ?',
            (address,)
        )
        wallet = await cursor.fetchone()
        
        if wallet:
            return {
                'id': wallet[0],
                'address': wallet[1],
                'points_balance': wallet[2],
                'locked_points': wallet[3],
                'total_deposited': wallet[4],
                'total_withdrawn': wallet[5],
                'created_at': wallet[6]
            }
        
        # Create new wallet
        cursor = await db.execute(
            'INSERT INTO human_wallets (address) VALUES (?)',
            (address,)
        )
        wallet_id = cursor.lastrowid
        await db.commit()
        
        return {
            'id': wallet_id,
            'address': address,
            'points_balance': 0.0,
            'locked_points': 0.0,
            'total_deposited': 0.0,
            'total_withdrawn': 0.0,
            'created_at': datetime.datetime.now().isoformat()
        }


async def update_human_wallet_balance(address: str, points_change: float, lock_points: float = 0.0):
    """
    Update human wallet points balance.
    
    Args:
        address: User address
        points_change: Points to add (positive) or deduct (negative)
        lock_points: Points to lock/unlock (for pending transactions)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE human_wallets SET 
                points_balance = points_balance + ?,
                locked_points = locked_points + ?
            WHERE address = ?
        ''', (points_change, lock_points, address))
        await db.commit()


async def record_deposit(user_address: str, wallet_address: str, tx_hash: str, amount: float):
    """
    Record a deposit transaction.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO deposits (user_address, wallet_address, tx_hash, amount, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (user_address, wallet_address, tx_hash, amount))
        deposit_id = cursor.lastrowid
        await db.commit()
        return deposit_id


async def confirm_deposit(tx_hash: str):
    """
    Confirm a deposit and update user balance.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Get deposit info
        cursor = await db.execute(
            'SELECT user_address, amount FROM deposits WHERE tx_hash = ?',
            (tx_hash,)
        )
        deposit = await cursor.fetchone()
        
        if not deposit:
            return False
        
        user_address, amount = deposit
        
        # Update deposit status
        await db.execute('''
            UPDATE deposits SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
            WHERE tx_hash = ?
        ''', (tx_hash,))
        
        # Update user balance
        await db.execute('''
            UPDATE human_wallets SET 
                points_balance = points_balance + ?,
                total_deposited = total_deposited + ?
            WHERE address = ?
        ''', (amount, amount, user_address))
        
        await db.commit()
        return True


async def record_withdrawal(user_address: str, amount: float, gas_fee: float = 0.0):
    """
    Record a withdrawal request.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO withdrawals (user_address, amount, gas_fee, status)
            VALUES (?, ?, ?, 'pending')
        ''', (user_address, amount, gas_fee))
        withdrawal_id = cursor.lastrowid
        await db.commit()
        return withdrawal_id


async def complete_withdrawal(withdrawal_id: int, tx_hash: str):
    """
    Complete a withdrawal after on-chain confirmation.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Get withdrawal info
        cursor = await db.execute(
            'SELECT user_address, amount FROM withdrawals WHERE id = ?',
            (withdrawal_id,)
        )
        withdrawal = await cursor.fetchone()
        
        if not withdrawal:
            return False
        
        user_address, amount = withdrawal
        
        # Update withdrawal status
        await db.execute('''
            UPDATE withdrawals SET 
                status = 'completed',
                tx_hash = ?,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (tx_hash, withdrawal_id))
        
        # Deduct from user balance
        await db.execute('''
            UPDATE human_wallets SET 
                points_balance = points_balance - ?,
                total_withdrawn = total_withdrawn + ?
            WHERE address = ?
        ''', (amount, amount, user_address))
        
        await db.commit()
        return True


# ============================================
# Product Management Functions
# ============================================

async def create_product(product_data: Dict[str, Any]) -> str:
    """
    Create a new micro-transaction product listing.
    Returns product_id.
    """
    import hashlib
    import json
    
    # Generate standardized contract hash (The "Promise")
    contract_str = f"{product_data['name']}|{product_data['description']}|{product_data['price']}|{product_data['delivery_hash']}"
    contract_hash = hashlib.sha256(contract_str.encode()).hexdigest()
    
    product_id = f"PROD_{product_data['seller_address'][:8]}_{int(datetime.datetime.now().timestamp())}"
    
    async with aiosqlite.connect(DB_PATH) as db:
        specs_json = json.dumps(product_data.get('specs', {}))
        
        await db.execute('''
            INSERT INTO products (
                product_id, seller_address, name, description, price, currency,
                category_id, specs_json, delivery_hash, contract_hash, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_id,
            product_data['seller_address'],
            product_data['name'],
            product_data['description'],
            product_data['price'],
            product_data.get('currency', 'TRX'),
            product_data['category_id'],
            specs_json,
            product_data['delivery_hash'],
            contract_hash,
            'active'
        ))
        
        await db.commit()
        return product_id


async def get_product(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get product details by product_id.
    """
    import json
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM products WHERE product_id = ?',
            (product_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        product = dict(zip(columns, row))
        
        # Parse JSON fields
        if product.get('specs_json'):
            product['specs'] = json.loads(product['specs_json'])
        
        return product


async def list_products(status: str = 'active', limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List products with pagination.
    """
    import json
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            '''SELECT * FROM products 
               WHERE status = ? 
               ORDER BY created_at DESC 
               LIMIT ? OFFSET ?''',
            (status, limit, offset)
        )
        rows = await cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        products = []
        
        for row in rows:
            product = dict(zip(columns, row))
            # Parse JSON fields
            if product.get('specs_json'):
                product['specs'] = json.loads(product['specs_json'])
            products.append(product)
        
        return products


async def update_product_status(product_id: str, status: str) -> bool:
    """
    Update product status (active, sold_out, suspended).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''UPDATE products SET status = ?, updated_at = CURRENT_TIMESTAMP
               WHERE product_id = ?''',
            (status, product_id)
        )
        await db.commit()
        return True


# ============================================
# Contract Management Functions
# ============================================

async def create_contract(contract_data: Dict[str, Any]) -> str:
    """
    Create a new contract when a transaction is initiated.
    Returns contract_id.
    """
    contract_id = f"CONTRACT_{int(datetime.datetime.now().timestamp())}_{contract_data['product_id'][:8]}"
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO contracts (
                contract_id, product_id, buyer_address, seller_address,
                contract_hash, file_hash, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            contract_id,
            contract_data['product_id'],
            contract_data.get('buyer_address', ''),
            contract_data['seller_address'],
            contract_data['contract_hash'],
            contract_data.get('file_hash', ''),
            'created'
        ))
        
        await db.commit()
        return contract_id


async def update_contract_anchor(contract_id: str, github_url: str, commit_sha: str) -> bool:
    """
    Update contract with GitHub anchor information.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE contracts SET 
                github_anchor_url = ?,
                github_commit_sha = ?,
                anchored_at = CURRENT_TIMESTAMP
            WHERE contract_id = ?
        ''', (github_url, commit_sha, contract_id))
        await db.commit()
        return True


async def update_contract_status(contract_id: str, status: str) -> bool:
    """
    Update contract status (created, active, completed, cancelled, disputed).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        if status == 'completed':
            await db.execute('''
                UPDATE contracts SET 
                    status = ?,
                    completed_at = CURRENT_TIMESTAMP
                WHERE contract_id = ?
            ''', (status, contract_id))
        else:
            await db.execute(
                'UPDATE contracts SET status = ? WHERE contract_id = ?',
                (status, contract_id)
            )
        await db.commit()
        return True


async def get_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    """
    Get contract details by contract_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM contracts WHERE contract_id = ?',
            (contract_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))


# ===== Reputation System Functions =====

async def update_reputation_score(
    address: str,
    score_change: int,
    reason: str = ""
) -> Dict[str, Any]:
    """
    Update user's reputation score with atomic behavior offset logic.
    
    Args:
        address: User wallet address
        score_change: Points to add (positive) or subtract (negative)
        reason: Reason for the change
        
    Returns:
        Updated reputation info
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Get current reputation
        cursor = await db.execute(
            'SELECT reputation_score, successful_streak FROM users WHERE address = ?',
            (address,)
        )
        row = await cursor.fetchone()
        
        if not row:
            # Create user if not exists
            current_score = 100
            streak = 0
            await db.execute(
                'INSERT INTO users (address, reputation_score, successful_streak) VALUES (?, ?, ?)',
                (address, current_score, streak)
            )
        else:
            current_score, streak = row
        
        # Apply Behavior Offset: If positive change, boost streak; if negative, reset streak
        new_streak = streak
        if score_change > 0:
            new_streak += 1
        elif score_change < 0:
            new_streak = 0
        
        # Calculate new score (clamp between 0-100)
        new_score = max(0, min(100, current_score + score_change))
        
        # Update score and streak
        await db.execute(
            'UPDATE users SET reputation_score = ?, successful_streak = ?, updated_at = CURRENT_TIMESTAMP WHERE address = ?',
            (new_score, new_streak, address)
        )
        
        # Record reputation history
        await db.execute('''
            INSERT INTO reputation_history 
            (user_address, score_change, new_score, reason)
            VALUES (?, ?, ?, ?)
        ''', (address, score_change, new_score, reason))
        
        await db.commit()
        
        return {
            "address": address,
            "previous_score": current_score,
            "score_change": score_change,
            "new_score": new_score,
            "new_streak": new_streak,
            "reason": reason
        }


async def calculate_margin_percentage(reputation_score: int) -> float:
    """
    Calculate margin percentage based on reputation score.
    Following Black2 Protocol Section 7.2.
    
    Args:
        reputation_score: User's reputation score (0-100)
        
    Returns:
        Margin percentage (5.0 - 20.0)
    """
    if reputation_score >= 90:
        return 5.0
    elif reputation_score >= 80:
        return 10.0
    elif reputation_score >= 70:
        return 15.0
    elif reputation_score >= 60:
        return 20.0
    else:
        return 0.0  # Cannot publish


async def get_arbitration_requirements(dispute_count: int) -> Dict[str, Any]:
    """
    Get arbitration requirements based on seller's dispute history (B2P Protocol).
    Returns required stake percentage and evidence submission deadline.
    """
    if dispute_count > 20:
        return {
            "stake_percentage": 0.20,  # 20% additional stake
            "deadline_hours": 0.5,     # 30 minutes
            "level": "high_risk"
        }
    elif dispute_count > 10:
        return {
            "stake_percentage": 0.10,  # 10% additional stake
            "deadline_hours": 12,      # 12 hours
            "level": "medium_risk"
        }
    elif dispute_count > 5:
        return {
            "stake_percentage": 0.05,  # 5% additional stake
            "deadline_hours": 24,      # 24 hours
            "level": "low_risk"
        }
    else:
        return {
            "stake_percentage": 0.0,
            "deadline_hours": 48,      # Standard 48 hours
            "level": "normal"
        }


async def execute_arbitration_verdict(tx_id: str, verdict: str, seller_address: str, dispute_count: int):
    """
    Execute the final verdict of an arbitration case.
    Handles fund redistribution and penalty collection for 'Thorn' sellers.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Get transaction details
        cursor = await db.execute('SELECT amount, buyer_address FROM transactions WHERE tx_id = ?', (tx_id,))
        tx = await cursor.fetchone()
        if not tx:
            return
        
        amount, buyer_address = tx
        
        if verdict == 'refund_buyer':
            # A. Refund principal to buyer (Protected)
            await db.execute(
                'UPDATE wallets SET balance = balance + ? WHERE address = ?',
                (amount, buyer_address)
            )
            
            # B. Apply Penalty to Seller (If Thorn)
            penalty = 0
            if dispute_count > 20:
                penalty = amount * 0.05  # 5% penalty from seller's stake
            elif dispute_count > 10:
                penalty = 2.0  # Fixed filing fee
            
            if penalty > 0:
                # Deduct from seller's wallet/stake
                await db.execute(
                    'UPDATE wallets SET balance = balance - ? WHERE address = ?',
                    (penalty, seller_address)
                )
                # Inject into Arbitration Fund
                await db.execute(
                    'INSERT INTO arbitration_fund_pool (amount, source_tx_id, reason) VALUES (?, ?, ?)',
                    (penalty, tx_id, f'Penalty for high-friction seller (disputes: {dispute_count})')
                )
                
            await db.execute('UPDATE transactions SET status = ? WHERE tx_id = ?', ('refunded', tx_id))
            
        elif verdict == 'release_seller':
            # A. Release principal + Additional Stake to seller (Vindication Loop)
            reqs = await get_arbitration_requirements(dispute_count)
            additional_stake = amount * reqs['stake_percentage']
            total_release = amount + additional_stake
            
            await db.execute(
                'UPDATE wallets SET balance = balance + ? WHERE address = ?',
                (total_release, seller_address)
            )
            
            # B. Reputation Repair: Increase successful streak & score
            await db.execute(
                'UPDATE users SET successful_streak = successful_streak + 1, reputation_score = MIN(100, reputation_score + 2) WHERE address = ?',
                (seller_address,)
            )
            
            await db.execute('UPDATE transactions SET status = ? WHERE tx_id = ?', ('completed', tx_id))
        
        await db.commit()
    """
    Calculate the cost and restrictions for initiating arbitration based on seller's history.
    Implements the 'Thorn' penalty logic from B2P Protocol.
    """
    cost = 0
    extra_stake_pct = 0
    
    if dispute_count > 20:
        # Level 3: High friction - Filing fee + Heavy stake
        cost = 5.0  # USDT filing fee
        extra_stake_pct = 0.10
    elif dispute_count > 10:
        # Level 2: Medium friction - Filing fee
        cost = 2.0  # USDT filing fee
    elif dispute_count > 5:
        # Level 1: Low friction - Extra stake required
        extra_stake_pct = 0.05
    
    return {
        "filing_fee": cost,
        "extra_stake_percentage": extra_stake_pct,
        "is_restricted": dispute_count > 20
    }


async def get_user_reputation_snapshot(address: str) -> Optional[Dict[str, Any]]:
    """
    O(1) Cache read for micro-transactions.
    Returns pre-computed reputation snapshot from reputation_cache table.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM reputation_cache WHERE address = ?',
            (address,)
        )
        row = await cursor.fetchone()
        
        if not row:
            # Return default snapshot for new users
            return {
                "address": address,
                "completion_rate": 1.0,
                "friction_index": 0.0,
                "risk_level": "low",
                "last_updated": None
            }
        
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))

async def update_reputation_cache_batch():
    """
    B2P-Indexer logic: Batch calculate and update reputation snapshots.
    Implements Time Decay + Completion Rate model.
    """
    import time
    now = time.time()
    window_7d = now - (7 * 24 * 3600)
    window_30d = now - (30 * 24 * 3600)

    async with aiosqlite.connect(DB_PATH) as db:
        # Get all active addresses from transactions in the last 30 days
        cursor = await db.execute('''
            SELECT DISTINCT buyer_address as address FROM transactions WHERE timestamp > ?
            UNION
            SELECT DISTINCT seller_address as address FROM transactions WHERE timestamp > ?
        ''', (window_30d, window_30d))
        
        rows = await cursor.fetchall()
        addresses = [row[0] for row in rows if row[0]]

        for addr in addresses:
            # Calculate stats for this address (as seller)
            total_cursor = await db.execute(
                'SELECT COUNT(*) FROM transactions WHERE to_address = ? AND timestamp > ?',
                (addr, window_30d)
            )
            total_count = (await total_cursor.fetchone())[0]
            
            success_cursor = await db.execute(
                'SELECT COUNT(*) FROM transactions WHERE to_address = ? AND status = ? AND timestamp > ?',
                (addr, 'completed', window_30d)
            )
            success_count = (await success_cursor.fetchone())[0]
            
            dispute_cursor = await db.execute(
                'SELECT COUNT(*) FROM arbitration_records WHERE seller_address = ? AND created_at > ?',
                (addr, window_30d)
            )
            dispute_count = (await dispute_cursor.fetchone())[0]

            if total_count == 0:
                continue

            # 1. Completion Rate
            completion_rate = success_count / total_count
            
            # 2. Friction Index (Simplified: disputes / total)
            friction_index = dispute_count / total_count
            
            # 3. Risk Level
            risk_level = "low"
            if friction_index > 0.15:
                risk_level = "high"
            elif friction_index > 0.05:
                risk_level = "medium"

            # Upsert into cache
            await db.execute('''
                INSERT OR REPLACE INTO reputation_cache 
                (address, completion_rate, friction_index, risk_level, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (addr, round(completion_rate, 4), round(friction_index, 4), risk_level, datetime.datetime.now().isoformat()))
        
        await db.commit()

async def get_user_reputation(address: str) -> Optional[Dict[str, Any]]:
    """
    Get user's current reputation info (Legacy/Full view).
    For micro-transactions, prefer using get_user_reputation_snapshot().
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT address, reputation_score, dispute_count, purchase_count, sales_count FROM users WHERE address = ?',
            (address,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        columns = [description[0] for description in cursor.description]
        user_data = dict(zip(columns, row))
        
        # Calculate margin percentage based on legacy score
        margin_pct = await calculate_margin_percentage(user_data['reputation_score'])
        user_data['margin_percentage'] = margin_pct
        user_data['can_publish'] = user_data['reputation_score'] >= 60
        
        return user_data


async def apply_transaction_reputation_update(
    tx_id: str,
    status: str,
    dispute_result: Optional[Dict[str, Any]] = None
):
    """
    Automatically update reputation scores after transaction completion.
    Following Black2 Protocol Section 7.1.
    
    Args:
        tx_id: Transaction ID
        status: Transaction status (completed, refunded, disputed)
        dispute_result: Optional dispute resolution result
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Get transaction details
        cursor = await db.execute(
            'SELECT buyer_address, seller_address FROM transactions WHERE tx_id = ?',
            (tx_id,)
        )
        tx = await cursor.fetchone()
        
        if not tx:
            return
        
        buyer_address, seller_address = tx
        
        # Update seller reputation based on outcome
        if status == 'completed':
            # Successful transaction: +1 point
            await update_reputation_score(
                seller_address,
                score_change=1,
                reason=f"Successful transaction {tx_id}"
            )
        elif status == 'refunded':
            # Refund: check if dispute
            if dispute_result:
                verdict = dispute_result.get('verdict', '')
                if verdict == 'seller_violation':
                    # Seller violation: -20 points
                    await update_reputation_score(
                        seller_address,
                        score_change=-20,
                        reason=f"Dispute lost: {dispute_result.get('reason', '')}"
                    )
                elif verdict == 'buyer_wins':
                    # Buyer wins: -15 points
                    await update_reputation_score(
                        seller_address,
                        score_change=-15,
                        reason=f"Dispute resolved against seller"
                    )
            else:
                # Voluntary refund: -5 points
                await update_reputation_score(
                    seller_address,
                    score_change=-5,
                    reason=f"Voluntary refund for transaction {tx_id}"
                )
