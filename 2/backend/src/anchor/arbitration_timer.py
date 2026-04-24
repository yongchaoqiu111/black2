"""
Arbitration Timer Service (Enhanced with Async Task Processor)

Manages automatic arbitration countdown for disputed transactions.
After 48 hours, automatically executes arbitration based on hash comparison.
Uses AsyncTaskProcessor for non-blocking fund release and anchoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ArbitrationTimerService:
    """
    Service for managing arbitration countdowns.
    Automatically executes arbitration after timeout.
    Uses AsyncTaskProcessor for non-blocking operations.
    """
    
    def __init__(self):
        self.countdowns: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.db_path: Optional[str] = None
        self.task_processor = None
        self.x402_bridge = None
        self.github_anchor = None
        self.x402_anchor = None
    
    def initialize(
        self,
        db_path: str,
        task_processor,
        x402_bridge,
        github_anchor,
        x402_anchor
    ):
        """
        Initialize with required services.
        """
        self.db_path = db_path
        self.task_processor = task_processor
        self.x402_bridge = x402_bridge
        self.github_anchor = github_anchor
        self.x402_anchor = x402_anchor
        logger.info("[Arbitration Timer] Service initialized")
    
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
        
        logger.info(f"[Arbitration] Started countdown for {tx_id} ({hours}h)")
        
        # Start background task
        asyncio.create_task(self._countdown_worker(tx_id))
    
    async def _countdown_worker(self, tx_id: str):
        """Background worker that monitors countdown."""
        while tx_id in self.countdowns:
            try:
                countdown = self.countdowns[tx_id]
                
                if countdown["status"] != "counting":
                    break
                
                time_remaining = countdown["deadline"] - datetime.now()
                
                if time_remaining.total_seconds() <= 0:
                    # Timeout reached
                    await self._handle_timeout(tx_id)
                    break
                
                # Check every 60 seconds
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"[Arbitration] Countdown worker error for {tx_id}: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _handle_timeout(self, tx_id: str):
        """
        Handle timeout based on arbitration status.
        - If 'refund_pending': seller didn't respond -> auto-approve refund
        - If 'evidence_collection' or 'arbitrating': execute arbitration
        """
        if tx_id not in self.countdowns:
            return
        
        try:
            import aiosqlite
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    'SELECT status FROM arbitration_records WHERE tx_id = ?',
                    (tx_id,)
                )
                record = await cursor.fetchone()
                
                if not record:
                    logger.warning(f"[Arbitration] No arbitration record for {tx_id}")
                    return
                
                arb_status = record[0]
                
                if arb_status == 'refund_pending':
                    # Seller didn't respond in 48h -> auto-approve refund
                    await self._auto_approve_refund(tx_id)
                else:
                    # Execute normal arbitration
                    await self._execute_arbitration(tx_id)
                    
        except Exception as e:
            logger.error(f"[Arbitration] Error handling timeout for {tx_id}: {e}", exc_info=True)
    
    async def _auto_approve_refund(self, tx_id: str):
        """
        Auto-approve refund when seller doesn't respond in 48 hours.
        Uses AsyncTaskProcessor for non-blocking operation.
        """
        import aiosqlite
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get transaction details
                cursor = await db.execute(
                    'SELECT from_address, to_address, amount, escrow_id FROM transactions WHERE tx_id = ?',
                    (tx_id,)
                )
                tx = await cursor.fetchone()
                
                if not tx:
                    logger.warning(f"[Arbitration] Transaction {tx_id} not found")
                    return
                
                buyer_addr, seller_addr, amount, escrow_id = tx
                
                logger.info(f"[Refund] Seller didn't respond for {tx_id}, auto-approving refund")
                
                # Update transaction status first
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
                
                # Increment dispute count
                await db.execute('''
                    UPDATE users SET dispute_count = dispute_count + 1
                    WHERE address IN (?, ?)
                ''', (buyer_addr, seller_addr))
                
                await db.commit()
                
                # Mark countdown as completed
                if tx_id in self.countdowns:
                    self.countdowns[tx_id]["status"] = "completed"
                
                logger.info(f"[Refund] Auto-approved refund for {tx_id}")
                
                # Use task processor to release funds and anchor
                if self.task_processor:
                    await self.task_processor.submit_task(
                        self._release_funds_and_anchor,
                        tx_id=tx_id,
                        verdict='buyer_wins',
                        escrow_id=escrow_id,
                        buyer_addr=buyer_addr,
                        seller_addr=seller_addr,
                        amount=amount
                    )
                
                # Call callback if provided
                countdown = self.countdowns.get(tx_id)
                if countdown and countdown.get("on_complete_callback"):
                    await countdown["on_complete_callback"](tx_id)
                
        except Exception as e:
            logger.error(f"[Arbitration] Error auto-approving refund for {tx_id}: {e}", exc_info=True)
    
    async def _execute_arbitration(self, tx_id: str):
        """
        Execute automatic arbitration when countdown expires.
        Compares contract_hash and file_hash to determine winner.
        Uses AsyncTaskProcessor for non-blocking operation.
        """
        if tx_id not in self.countdowns:
            return
        
        import aiosqlite
        countdown = self.countdowns[tx_id]
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get transaction details
                cursor = await db.execute(
                    'SELECT contract_hash, file_hash, amount, from_address, to_address, escrow_id FROM transactions WHERE tx_id = ?',
                    (tx_id,)
                )
                tx = await cursor.fetchone()
                
                if not tx:
                    logger.warning(f"[Arbitration] Transaction {tx_id} not found")
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
                
                logger.info(f"[Arbitration] Verdict for {tx_id}: {verdict} - {verdict_reason}")
                
                # Update arbitration record
                await db.execute('''
                    UPDATE arbitration_records 
                    SET verdict = ?, verdict_reason = ?, status = 'completed', resolved_at = ?
                    WHERE tx_id = ?
                ''', (verdict, verdict_reason, datetime.now().isoformat(), tx_id))
                
                # Execute verdict
                if verdict == "buyer_wins":
                    # Refund buyer
                    await db.execute(
                        'UPDATE transactions SET status = ? WHERE tx_id = ?',
                        ('refunded', tx_id)
                    )
                    
                    # Deduct seller reputation
                    await db.execute('''
                        UPDATE users SET reputation_score = MAX(0, reputation_score - 10)
                        WHERE address = ?
                    ''', (seller_addr,))
                    
                    # Cancel referral settlement (mark as cancelled)
                    await db.execute('''
                        UPDATE transaction_referrals 
                        SET settlement_status = 'cancelled'
                        WHERE tx_id = ?
                    ''', (tx_id,))
                    
                    logger.info(f"[Arbitration] Refunded {amount} to buyer {buyer_addr}")
                    
                else:  # seller_wins
                    # Complete transaction
                    await db.execute(
                        'UPDATE transactions SET status = ? WHERE tx_id = ?',
                        ('completed', tx_id)
                    )
                    
                    logger.info(f"[Arbitration] Seller wins for {tx_id}")
                
                # Increment dispute count for both parties
                await db.execute('''
                    UPDATE users SET dispute_count = dispute_count + 1
                    WHERE address IN (?, ?)
                ''', (buyer_addr, seller_addr))
                
                await db.commit()
                
                # Mark countdown as completed
                countdown["status"] = "completed"
                
                logger.info(f"[Arbitration] Automatic arbitration completed for {tx_id}")
                
                # Use task processor to release funds and anchor
                if self.task_processor:
                    await self.task_processor.submit_task(
                        self._release_funds_and_anchor,
                        tx_id=tx_id,
                        verdict=verdict,
                        escrow_id=escrow_id,
                        buyer_addr=buyer_addr,
                        seller_addr=seller_addr,
                        amount=amount
                    )
                
                # Call callback if provided
                if countdown.get("on_complete_callback"):
                    await countdown["on_complete_callback"](tx_id)
                
        except Exception as e:
            logger.error(f"[Arbitration] Error executing arbitration for {tx_id}: {e}", exc_info=True)
            countdown["status"] = "error"
    
    async def _release_funds_and_anchor(
        self,
        tx_id: str,
        verdict: str,
        escrow_id: Optional[str],
        buyer_addr: str,
        seller_addr: str,
        amount: float
    ):
        """
        Release funds via X402 and anchor the result.
        This function runs in a background task to avoid blocking.
        """
        import aiosqlite
        try:
            logger.info(f"[Arbitration] Starting fund release for {tx_id}, verdict: {verdict}")
            
            recipient = seller_addr if verdict == "seller_wins" else buyer_addr
            
            # Step 1: Release funds via X402
            x402_tx_hash = None
            if self.x402_bridge and escrow_id:
                try:
                    x402_result = await self.x402_bridge.release_funds(
                        escrow_id=escrow_id,
                        recipient=recipient,
                        verdict=verdict
                    )
                    x402_tx_hash = x402_result.get("tx_hash")
                    logger.info(f"[X402] Funds released for {tx_id}: {x402_tx_hash}")
                except Exception as e:
                    logger.error(f"[X402] Failed to release funds for {tx_id}: {e}", exc_info=True)
                    raise  # Re-raise to trigger retry
            
            # Step 2: Update transaction record with X402 tx hash
            async with aiosqlite.connect(self.db_path) as db:
                if verdict == "seller_wins":
                    # Credit seller's local wallet (for non-X402 fallback)
                    await db.execute('''
                        UPDATE ai_wallets SET 
                            balance = balance + ?,
                            total_received = total_received + ?
                        WHERE address = ?
                    ''', (amount, amount, seller_addr))
                else:
                    # Refund buyer's local wallet
                    await db.execute('''
                        UPDATE ai_wallets SET 
                            balance = balance + ?,
                            total_refunded = total_refunded + ?
                        WHERE address = ?
                    ''', (amount, amount, buyer_addr))
                
                # Update X402 tx hash on transaction
                if x402_tx_hash:
                    await db.execute(
                        'UPDATE transactions SET x402_tx_hash = ? WHERE tx_id = ?',
                        (x402_tx_hash, tx_id)
                    )
                
                # Settle referrals if seller wins
                if verdict == "seller_wins":
                    try:
                        from src.db.transaction_db import settle_referral_rewards
                        await settle_referral_rewards(tx_id, db)
                    except Exception as e:
                        logger.error(f"[Arbitration] Failed to settle referrals for {tx_id}: {e}")
                
                await db.commit()
            
            # Step 3: Anchor result to GitHub
            github_commit_hash = None
            if self.github_anchor:
                try:
                    content = {
                        "type": "arbitration_result",
                        "tx_id": tx_id,
                        "verdict": verdict,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "x402_tx_hash": x402_tx_hash
                    }
                    import json
                    result = await self.github_anchor.anchor_arbitration_result(
                        arbitration_id=tx_id,
                        verdict=verdict,
                        metadata=content
                    )
                    github_commit_hash = result.get("sha")
                    logger.info(f"[GitHub] Anchored result for {tx_id}: {github_commit_hash}")
                except Exception as e:
                    logger.error(f"[GitHub] Failed to anchor for {tx_id}: {e}", exc_info=True)
                    # Don't fail the whole process for this
            
            # Step 4: Optionally anchor to X402 as backup
            if self.x402_anchor and github_commit_hash:
                try:
                    x402_anchor_result = await self.x402_anchor.anchor_commit_hash(
                        commit_hash=github_commit_hash,
                        anchor_type="arbitration",
                        metadata={"tx_id": tx_id, "verdict": verdict}
                    )
                    if x402_anchor_result.get("success"):
                        logger.info(f"[X402 Chain] Secondary anchor completed for {tx_id}")
                except Exception as e:
                    logger.warning(f"[X402 Chain] Secondary anchor failed: {e}")
                    # Don't fail the whole process for this
            
            logger.info(f"[Arbitration] Fund release complete for {tx_id}")
            
        except Exception as e:
            logger.error(f"[Arbitration] Failed to release funds for {tx_id}: {e}", exc_info=True)
            raise  # Re-raise to trigger retry
    
    async def execute_arbitration_verdict(
        self,
        tx_id: str,
        verdict: str
    ):
        """
        Manual trigger: Execute arbitration verdict.
        Uses AsyncTaskProcessor to avoid blocking API response.
        """
        import aiosqlite
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get transaction details
                cursor = await db.execute(
                    'SELECT amount, from_address, to_address, escrow_id FROM transactions WHERE tx_id = ?',
                    (tx_id,)
                )
                tx = await cursor.fetchone()
                
                if not tx:
                    raise ValueError(f"Transaction {tx_id} not found")
                
                amount, buyer_addr, seller_addr, escrow_id = tx
                
                # Update arbitration record
                await db.execute('''
                    UPDATE arbitration_records 
                    SET status = 'completed', verdict = ?, resolved_at = ?
                    WHERE tx_id = ?
                ''', (verdict, datetime.now().isoformat(), tx_id))
                
                # Update transaction status
                status = "completed" if verdict == "seller_wins" else "refunded"
                await db.execute(
                    'UPDATE transactions SET status = ? WHERE tx_id = ?',
                    (status, tx_id)
                )
                
                await db.commit()
                
                # Cancel any running countdown
                if tx_id in self.countdowns:
                    self.countdowns[tx_id]["status"] = "completed"
                
                logger.info(f"[Arbitration] Manual verdict executed for {tx_id}")
                
                # Submit to task processor for non-blocking fund release
                if self.task_processor:
                    await self.task_processor.submit_task(
                        self._release_funds_and_anchor,
                        tx_id=tx_id,
                        verdict=verdict,
                        escrow_id=escrow_id,
                        buyer_addr=buyer_addr,
                        seller_addr=seller_addr,
                        amount=amount
                    )
                
        except Exception as e:
            logger.error(f"[Arbitration] Error executing verdict for {tx_id}: {e}", exc_info=True)
            raise
    
    async def cancel_countdown(self, tx_id: str):
        """
        Cancel countdown (e.g., when seller submits evidence early).
        """
        if tx_id in self.countdowns:
            self.countdowns[tx_id]["status"] = "cancelled"
            del self.countdowns[tx_id]
            logger.info(f"[Arbitration] Countdown cancelled for {tx_id}")
    
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
        if not self.db_path:
            logger.warning("[Arbitration Timer] Database path not set, skipping initialization")
            return
        
        import aiosqlite
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    SELECT tx_id, deadline FROM arbitration_records 
                    WHERE status IN ('evidence_collection', 'arbitrating', 'refund_pending')
                ''')
                
                records = await cursor.fetchall()
                
                initialized_count = 0
                for tx_id, deadline in records:
                    try:
                        # Calculate remaining hours
                        deadline_dt = datetime.fromisoformat(deadline)
                        remaining = (deadline_dt - datetime.now()).total_seconds() / 3600
                        
                        if remaining > 0:
                            await self.start_arbitration_countdown(tx_id, hours=remaining)
                            logger.debug(f"[Arbitration] Resumed countdown for {tx_id} ({remaining:.1f}h remaining)")
                            initialized_count += 1
                    except Exception as e:
                        logger.error(f"[Arbitration] Failed to resume countdown for {tx_id}: {e}")
                
                logger.info(f"[Arbitration] Initialized {initialized_count} pending arbitrations")
                
        except Exception as e:
            logger.error(f"[Arbitration] Failed to initialize pending arbitrations: {e}", exc_info=True)


# Global instance
arbitration_timer_service = ArbitrationTimerService()
