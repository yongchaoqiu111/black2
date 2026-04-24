"""
Arbitration Timer Service with X402 Integration

Manages automatic arbitration countdown for disputed transactions.
After 48 hours, automatically executes arbitration based on hash comparison.
Integrates with X402 protocol for escrow fund release.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiosqlite
import os

DB_PATH = os.getenv('DB_PATH', 'black2.db')


class ArbitrationTimerService:
    """
    Service for managing arbitration countdowns.
    Automatically executes arbitration after timeout.
    Integrates with X402 for fund release.
    """
    
    def __init__(self):
        self.countdowns: Dict[str, Dict[str, Any]] = {}
        self.running = False
    
    async def start_arbitration_countdown(
        self,
        tx_id: str,
        hours: int = 48,
        on_complete_callback=None
    ):
        """
        Start arbitration countdown for a disputed transaction.
        
        Args:
            tx_id: Transaction ID
            hours: Hours until automatic arbitration (default: 48)
            on_complete_callback: Async function to call when countdown completes
        """
        deadline = datetime.now() + timedelta(hours=hours)
        
        self.countdowns[tx_id] = {
            "tx_id": tx_id,
            "deadline": deadline,
            "hours": hours,
            "status": "counting",
            "on_complete_callback": on_complete_callback
        }
        
        asyncio.create_task(self._countdown_worker(tx_id))
    
    async def _countdown_worker(self, tx_id: str):
        """Background worker that monitors countdown."""
        while tx_id in self.countdowns:
            countdown = self.countdowns[tx_id]
            
            if countdown["status"] != "counting":
                break
            
            time_remaining = countdown["deadline"] - datetime.now()
            
            if time_remaining.total_seconds() <= 0:
                await self._handle_timeout(tx_id)
                break
            
            await asyncio.sleep(60)
    
    async def _handle_timeout(self, tx_id: str):
        """
        Handle timeout based on arbitration status.
        - If 'refund_pending': seller didn't respond -> auto-approve refund
        - If 'evidence_collection' or 'arbitrating': execute arbitration
        """
        if tx_id not in self.countdowns:
            return
        
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute(
                    'SELECT status FROM arbitration_records WHERE tx_id = ?',
                    (tx_id,)
                )
                record = await cursor.fetchone()
                
                if not record:
                    print(f"[Arbitration] No arbitration record for {tx_id}")
                    return
                
                arb_status = record[0]
                
                if arb_status == 'refund_pending':
                    await self._auto_approve_refund(tx_id)
                else:
                    await self._execute_arbitration(tx_id)
                    
        except Exception as e:
            print(f"[Arbitration] Error handling timeout for {tx_id}: {e}")
    
    async def _auto_approve_refund(self, tx_id: str):
        """
        Auto-approve refund when seller doesn't respond in 48 hours.
        Integrates with X402 to release escrow funds.
        """
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute(
                    'SELECT from_address, to_address, amount, x402_escrow_id FROM transactions WHERE tx_id = ?',
                    (tx_id,)
                )
                tx = await cursor.fetchone()
                
                if not tx:
                    print(f"[Arbitration] Transaction {tx_id} not found")
                    return
                
                buyer_addr, seller_addr, amount, escrow_id = tx
                
                print(f"[Refund] Seller didn't respond for {tx_id}, auto-approving refund")
                
                # Release funds via X402 Bridge
                await self._release_funds_via_x402(tx_id, escrow_id, buyer_addr, "buyer_wins")
                
                # Refund to buyer's AI wallet
                await db.execute(
                    'UPDATE ai_wallets SET balance = balance + ? WHERE address = ?',
                    (amount, buyer_addr)
                )
                
                # Update transaction status
                await db.execute(
                    'UPDATE transactions SET status = ? WHERE tx_id = ?',
                    ('refunded', tx_id)
                )
                
                # Cancel referral rewards
                await db.execute('''
                    UPDATE transaction_referrals
                    SET settlement_status = 'cancelled'
                    WHERE tx_id = ?
                ''', (tx_id,))
                
                # Update arbitration record
                await db.execute('''
                    UPDATE arbitration_records
                    SET status = 'completed', verdict = 'buyer_wins',
                        verdict_reason = 'Seller did not respond within 48 hours',
                        resolved_at = ?
                    WHERE tx_id = ?
                ''', (datetime.now().isoformat(), tx_id))
                
                await db.commit()
                
                if tx_id in self.countdowns:
                    self.countdowns[tx_id]["status"] = "completed"
                
                print(f"[Refund] Auto-approved refund for {tx_id}")
                
        except Exception as e:
            print(f"[Arbitration] Error auto-approving refund for {tx_id}: {e}")
    
    async def _execute_arbitration(self, tx_id: str):
        """
        Execute automatic arbitration when countdown expires.
        Compares contract_hash and file_hash to determine winner.
        Integrates with X402 for fund release.
        """
        if tx_id not in self.countdowns:
            return
        
        countdown = self.countdowns[tx_id]
        
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute(
                    'SELECT contract_hash, file_hash, amount, from_address, to_address, x402_escrow_id FROM transactions WHERE tx_id = ?',
                    (tx_id,)
                )
                tx = await cursor.fetchone()
                
                if not tx:
                    print(f"[Arbitration] Transaction {tx_id} not found")
                    return
                
                contract_hash, file_hash, amount, buyer_addr, seller_addr, escrow_id = tx
                
                # Arbitration logic: compare hashes
                if not file_hash:
                    verdict = "buyer_wins"
                    verdict_reason = "Seller did not deliver the file"
                elif contract_hash == file_hash:
                    verdict = "seller_wins"
                    verdict_reason = "Contract hash matches delivered file"
                else:
                    verdict = "buyer_wins"
                    verdict_reason = "Delivered file hash does not match contract hash"
                
                print(f"[Arbitration] Verdict for {tx_id}: {verdict} - {verdict_reason}")
                
                # Update arbitration record
                await db.execute('''
                    UPDATE arbitration_records
                    SET verdict = ?, verdict_reason = ?, status = 'completed', resolved_at = ?
                    WHERE tx_id = ?
                ''', (verdict, verdict_reason, datetime.now().isoformat(), tx_id))
                
                # Execute verdict with X402 fund release
                if verdict == "buyer_wins":
                    await db.execute(
                        'UPDATE transactions SET status = ? WHERE tx_id = ?',
                        ('refunded', tx_id)
                    )
                    
                    await db.execute('''
                        UPDATE ai_wallets SET
                            balance = balance + ?,
                            total_refunded = total_refunded + ?
                        WHERE address = ?
                    ''', (amount, amount, buyer_addr))
                    
                    await db.execute('''
                        UPDATE users SET reputation_score = MAX(0, reputation_score - 10)
                        WHERE address = ?
                    ''', (seller_addr,))
                    
                    await db.execute('''
                        UPDATE transaction_referrals
                        SET settlement_status = 'cancelled'
                        WHERE tx_id = ?
                    ''', (tx_id,))
                    
                    # Release funds to buyer via X402
                    await self._release_funds_via_x402(tx_id, escrow_id, buyer_addr, verdict)
                    
                    print(f"[Arbitration] Refunded {amount} to buyer {buyer_addr}")
                    
                else:  # seller_wins
                    await db.execute(
                        'UPDATE transactions SET status = ? WHERE tx_id = ?',
                        ('completed', tx_id)
                    )
                    
                    from src.db.transaction_db import settle_referral_rewards
                    await settle_referral_rewards(tx_id)
                    
                    # Release funds to seller via X402
                    await self._release_funds_via_x402(tx_id, escrow_id, seller_addr, verdict)
                    
                    print(f"[Arbitration] Seller wins, referrals settled for {tx_id}")
                
                await db.execute('''
                    UPDATE users SET dispute_count = dispute_count + 1
                    WHERE address IN (?, ?)
                ''', (buyer_addr, seller_addr))
                
                await db.commit()
                
                countdown["status"] = "completed"
                
                if countdown.get("on_complete_callback"):
                    await countdown["on_complete_callback"](tx_id)
                
                print(f"[Arbitration] Automatic arbitration completed for {tx_id}")
                
        except Exception as e:
            print(f"[Arbitration] Error executing arbitration for {tx_id}: {e}")
            countdown["status"] = "error"
    
    async def _release_funds_via_x402(
        self,
        tx_id: str,
        escrow_id: str,
        recipient: str,
        verdict: str
    ):
        """
        Release funds via X402 Bridge.
        HOOK: This integrates with the X402 protocol for fund release.
        """
        if not escrow_id:
            print(f"[X402] No escrow_id for {tx_id}, skipping X402 release")
            return
        
        try:
            from src.x402.bridge import x402_bridge
            
            if x402_bridge.is_available():
                result = await x402_bridge.release_funds(
                    escrow_id=escrow_id,
                    recipient=recipient,
                    verdict=verdict
                )
                
                print(f"[X402] Fund release result for {tx_id}: {result.message}")
                
                if result.tx_hash:
                    print(f"[X402] TX Hash: {result.tx_hash}")
            else:
                print(f"[X402] X402 Bridge not available, using local release for {tx_id}")
                
        except ImportError:
            print(f"[X402] X402 Bridge not found, using local release for {tx_id}")
        except Exception as e:
            print(f"[X402] Error releasing funds for {tx_id}: {e}")
    
    async def cancel_countdown(self, tx_id: str):
        """
        Cancel countdown (e.g., when seller submits evidence early).
        """
        if tx_id in self.countdowns:
            self.countdowns[tx_id]["status"] = "cancelled"
            del self.countdowns[tx_id]
            print(f"[Arbitration] Countdown cancelled for {tx_id}")
    
    def get_countdown_status(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current countdown status for a transaction.
        """
        if tx_id not in self.countdowns:
            return None
        
        countdown = self.countdowns[tx_id]
        time_remaining = (countdown["deadline"] - datetime.now()).total_seconds()
        
        return {
            "tx_id": tx_id,
            "time_remaining_seconds": max(0, time_remaining),
            "hours": countdown["hours"],
            "status": countdown["status"],
            "deadline": countdown["deadline"].isoformat()
        }
    
    async def initialize_pending_arbitrations(self):
        """
        Initialize countdowns for pending arbitrations from database.
        Call this on server startup.
        """
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute('''
                    SELECT tx_id, deadline FROM arbitration_records
                    WHERE status IN ('evidence_collection', 'arbitrating')
                    AND deadline > ?
                ''', (datetime.now().isoformat(),))
                
                records = await cursor.fetchall()
                
                for tx_id, deadline in records:
                    deadline_dt = datetime.fromisoformat(deadline)
                    remaining = (deadline_dt - datetime.now()).total_seconds() / 3600
                    
                    if remaining > 0:
                        await self.start_arbitration_countdown(tx_id, hours=remaining)
                        print(f"[Arbitration] Resumed countdown for {tx_id} ({remaining:.1f}h remaining)")
                
                print(f"[Arbitration] Initialized {len(records)} pending arbitrations")
                
        except Exception as e:
            print(f"[Arbitration] Failed to initialize pending arbitrations: {e}")


arbitration_timer_service = ArbitrationTimerService()
