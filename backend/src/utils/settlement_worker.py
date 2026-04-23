"""
Settlement worker tasks for processing referral rewards.
"""
import aiosqlite
import asyncio
from datetime import datetime

DB_PATH = 'black2.db'


def process_referral_creation(tx_id: str, tu1_addr: str, tu1_amount: float,
                               tu2_addr: str, tu2_amount: float,
                               tu3_addr: str, tu3_amount: float):
    """
    Create referral record in transaction_referrals table.
    Called by RQ worker when order is created (Async Pre-write).
    """
    print(f"[Referral Worker] Creating referral record for order {tx_id}")
    asyncio.run(_process_referral_creation_async(
        tx_id, tu1_addr, tu1_amount,
        tu2_addr, tu2_amount,
        tu3_addr, tu3_amount
    ))


async def _process_referral_creation_async(tx_id: str, tu1_addr: str, tu1_amount: float,
                                            tu2_addr: str, tu2_amount: float,
                                            tu3_addr: str, tu3_amount: float):
    """Async implementation of referral creation."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute('''
                INSERT INTO transaction_referrals 
                (tx_id, tu1_address, tu1_amount, tu2_address, tu2_amount, 
                 tu3_address, tu3_amount, settlement_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tx_id, tu1_addr if tu1_addr else None, tu1_amount,
                  tu2_addr if tu2_addr else None, tu2_amount,
                  tu3_addr if tu3_addr else None, tu3_amount,
                  'pending'))
            
            await db.commit()
            print(f"[Referral Worker] Referral record created for {tx_id}")
            
        except Exception as e:
            await db.rollback()
            print(f"[Referral Worker] Error creating referral for {tx_id}: {e}")
            raise


def process_settlement(order_id: str, seller_addr: str, seller_amount: float,
                       tu1_addr: str, tu1_amount: float,
                       tu2_addr: str, tu2_amount: float,
                       tu3_addr: str, tu3_amount: float):
    """
    Process settlement for a single order.
    This function is called by RQ worker (sequential processing).
    """
    print(f"[Settlement Worker] Processing order {order_id}")
    
    # Run async function in sync context
    asyncio.run(_process_settlement_async(
        order_id, seller_addr, seller_amount,
        tu1_addr, tu1_amount,
        tu2_addr, tu2_amount,
        tu3_addr, tu3_amount
    ))


async def _process_settlement_async(order_id: str, seller_addr: str, seller_amount: float,
                                     tu1_addr: str, tu1_amount: float,
                                     tu2_addr: str, tu2_amount: float,
                                     tu3_addr: str, tu3_amount: float):
    """Async implementation of settlement processing."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            # 1. Credit seller AI wallet (90%) - Atomic Update
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
                (datetime.utcnow().isoformat(), order_id)
            )
            
            await db.commit()
            print(f"[Settlement Worker] Order {order_id} completed successfully")
            
        except Exception as e:
            await db.rollback()
            print(f"[Settlement Worker] Error processing order {order_id}: {e}")
            # Mark as failed
            await db.execute(
                "UPDATE transaction_referrals SET settlement_status = 'failed' WHERE tx_id = ?",
                (order_id,)
            )
            await db.commit()
            raise
