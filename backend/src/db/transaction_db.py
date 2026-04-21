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
        
        # Create deposits table (on-chain deposit records)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_address TEXT NOT NULL,
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
        
        # Create products table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                seller_address TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                category TEXT,
                version TEXT,
                system_requirements TEXT,
                contract_template TEXT,
                metrics TEXT,  -- JSON array of quantifiable metrics
                file_hash TEXT,
                delivery_method TEXT,
                auto_confirm_hours INTEGER DEFAULT 72,
                storage_plan TEXT,
                delivery_checklist TEXT,  -- JSON object
                reputation_score INTEGER DEFAULT 100,
                margin_percentage REAL DEFAULT 5.0,
                status TEXT DEFAULT 'active',  -- active, sold_out, suspended
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
        
        # Create users table (for reputation system)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                reputation_score INTEGER DEFAULT 100,
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
                """SELECT hash as tx_hash, from_address as sender, to_address as receiver, amount, 0.0 as fee, timestamp
                   FROM transactions
                   WHERE anchor_hash IS NULL
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
                        "timestamp": row[5]
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
    Get a transaction by tx_id.
    
    Args:
        tx_id: Transaction ID
        
    Returns:
        Transaction dictionary or None if not found
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT * FROM transactions WHERE tx_id = ?
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
        List of transaction dictionaries
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Build query
        query = 'SELECT * FROM transactions WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if from_address:
            query += ' AND from_address = ?'
            params.append(from_address)
        
        if to_address:
            query += ' AND to_address = ?'
            params.append(to_address)
        
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
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
    Distribute points to referrers.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Get all pending rewards for this transaction
        cursor = await db.execute('''
            SELECT id, referrer_address, reward_amount, level
            FROM referral_rewards
            WHERE tx_id = ? AND status = 'pending'
        ''', (tx_id,))
        
        rewards = await cursor.fetchall()
        
        for reward in rewards:
            reward_id, referrer_address, amount, level = reward
            
            # Update reward status to completed
            await db.execute('''
                UPDATE referral_rewards SET 
                    status = 'completed',
                    settled_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (reward_id,))
            
            # Add points to referrer's AI wallet
            await db.execute('''
                UPDATE ai_wallets SET 
                    balance = balance + ?,
                    total_earned = total_earned + ?,
                    referral_count = referral_count + 1
                WHERE address = ?
            ''', (amount, amount, referrer_address))
        
        await db.commit()
        return len(rewards)


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


async def calculate_referral_chain(buyer_address: str) -> List[str]:
    """
    Calculate 5-level referral chain for a buyer.
    
    Args:
        buyer_address: Buyer's address
        
    Returns:
        List of referrer addresses in order (level 1 to 5)
    """
    chain = []
    current_address = buyer_address
    
    async with aiosqlite.connect(DB_PATH) as db:
        for level in range(5):
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


async def record_deposit(user_address: str, tx_hash: str, amount: float):
    """
    Record a deposit transaction.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO deposits (user_address, tx_hash, amount, status)
            VALUES (?, ?, ?, 'pending')
        ''', (user_address, tx_hash, amount))
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
    Create a new product listing.
    Returns product_id.
    """
    import json
    
    product_id = f"PROD_{product_data['seller_address'][:8]}_{int(datetime.datetime.now().timestamp())}"
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Convert metrics and delivery_checklist to JSON strings
        metrics_json = json.dumps(product_data.get('metrics', []))
        checklist_json = json.dumps(product_data.get('delivery_checklist', {}))
        
        await db.execute('''
            INSERT INTO products (
                product_id, seller_address, name, description, price, currency,
                category, version, system_requirements, contract_template,
                metrics, file_hash, delivery_method, auto_confirm_hours,
                storage_plan, delivery_checklist, reputation_score, margin_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_id,
            product_data['seller_address'],
            product_data['name'],
            product_data.get('description', ''),
            product_data['price'],
            product_data.get('currency', 'USD'),
            product_data.get('category', ''),
            product_data.get('version', ''),
            product_data.get('system_requirements', ''),
            product_data.get('contract_template', ''),
            metrics_json,
            product_data.get('file_hash', ''),
            product_data.get('delivery_method', ''),
            product_data.get('auto_confirm_hours', 72),
            product_data.get('storage_plan', ''),
            checklist_json,
            product_data.get('reputation_score', 100),
            product_data.get('margin_percentage', 5.0)
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
        if product.get('metrics'):
            product['metrics'] = json.loads(product['metrics'])
        if product.get('delivery_checklist'):
            product['delivery_checklist'] = json.loads(product['delivery_checklist'])
        
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
            if product.get('metrics'):
                product['metrics'] = json.loads(product['metrics'])
            if product.get('delivery_checklist'):
                product['delivery_checklist'] = json.loads(product['delivery_checklist'])
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
    Update user's reputation score.
    
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
            'SELECT reputation_score FROM users WHERE address = ?',
            (address,)
        )
        row = await cursor.fetchone()
        
        if not row:
            # Create user if not exists
            current_score = 100
            await db.execute(
                'INSERT INTO users (address, reputation_score) VALUES (?, ?)',
                (address, current_score)
            )
        else:
            current_score = row[0]
        
        # Calculate new score (clamp between 0-100)
        new_score = max(0, min(100, current_score + score_change))
        
        # Update score
        await db.execute(
            'UPDATE users SET reputation_score = ?, updated_at = CURRENT_TIMESTAMP WHERE address = ?',
            (new_score, address)
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


async def get_user_reputation(address: str) -> Optional[Dict[str, Any]]:
    """
    Get user's current reputation info.
    
    Args:
        address: User wallet address
        
    Returns:
        User reputation data or None
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT address, reputation_score, created_at, updated_at FROM users WHERE address = ?',
            (address,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        columns = [description[0] for description in cursor.description]
        user_data = dict(zip(columns, row))
        
        # Calculate margin percentage
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
