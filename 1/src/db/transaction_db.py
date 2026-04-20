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
        
        # Create referral_rewards table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS referral_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT NOT NULL,
                referrer_address TEXT NOT NULL,
                reward_amount REAL NOT NULL,
                level INTEGER NOT NULL,
                paid BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.commit()


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
    level: int
) -> Dict[str, Any]:
    """
    Add a referral reward record.
    
    Args:
        tx_id: Transaction ID
        referrer_address: Referrer address
        amount: Reward amount
        level: Referral level (1-5)
        
    Returns:
        Created reward record
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Insert reward
        cursor = await db.execute('''
            INSERT INTO referral_rewards (
                tx_id, referrer_address, reward_amount, level
            ) VALUES (?, ?, ?, ?)
        ''', (tx_id, referrer_address, amount, level))
        
        reward_id = cursor.lastrowid
        await db.commit()
        
        # Update wallet balance and referral count
        await db.execute('''
            UPDATE ai_wallets SET 
                balance = balance + ?, 
                total_earned = total_earned + ?, 
                referral_count = referral_count + 1
            WHERE address = ?
        ''', (amount, amount, referrer_address))
        await db.commit()
        
        # Return the created reward
        return {
            'id': reward_id,
            'tx_id': tx_id,
            'referrer_address': referrer_address,
            'reward_amount': amount,
            'level': level,
            'paid': False,
            'created_at': datetime.datetime.now().isoformat()
        }


async def calculate_referral_chain(buyer_address: str) -> List[str]:
    """
    Calculate 5-level referral chain for a buyer.
    
    Args:
        buyer_address: Buyer's address
        
    Returns:
        List of referrer addresses in order (level 1 to 5)
    """
    # This is a simplified implementation
    # In a real system, you would need a way to track the referral chain
    # For this challenge, we'll return an empty list as placeholder
    return []
