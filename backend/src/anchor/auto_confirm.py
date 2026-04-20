"""
Auto-Confirm Service

Manages automatic confirmation countdown for transactions.
Following Black2 Protocol Section 2.7 Rule 4.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from src.db.transaction_db import update_transaction_status, settle_referral_rewards


class AutoConfirmService:
    """
    Service for managing auto-confirm countdowns.
    Automatically completes transactions after timeout if no dispute is raised.
    """
    
    def __init__(self):
        self.countdowns: Dict[str, Dict[str, Any]] = {}
        self.running = False
    
    async def start_countdown(
        self,
        tx_id: str,
        auto_confirm_hours: int = 72,
        on_complete_callback=None
    ):
        """
        Start auto-confirm countdown for a transaction.
        
        Args:
            tx_id: Transaction ID
            auto_confirm_hours: Hours until auto-confirm (24-168)
            on_complete_callback: Async function to call when countdown completes
        """
        # Validate hours range
        if not 24 <= auto_confirm_hours <= 168:
            raise ValueError("auto_confirm_hours must be between 24 and 168")
        
        deadline = datetime.now() + timedelta(hours=auto_confirm_hours)
        
        self.countdowns[tx_id] = {
            "tx_id": tx_id,
            "deadline": deadline,
            "auto_confirm_hours": auto_confirm_hours,
            "status": "counting",
            "on_complete_callback": on_complete_callback
        }
        
        # Start background task
        asyncio.create_task(self._countdown_worker(tx_id))
    
    async def _countdown_worker(self, tx_id: str):
        """Background worker that monitors countdown."""
        while tx_id in self.countdowns:
            countdown = self.countdowns[tx_id]
            
            if countdown["status"] != "counting":
                break
            
            time_remaining = countdown["deadline"] - datetime.now()
            
            if time_remaining.total_seconds() <= 0:
                # Timeout reached - auto confirm
                await self._auto_confirm(tx_id)
                break
            
            # Check every 60 seconds
            await asyncio.sleep(60)
    
    async def _auto_confirm(self, tx_id: str):
        """
        Execute auto-confirm when countdown expires.
        """
        if tx_id not in self.countdowns:
            return
        
        countdown = self.countdowns[tx_id]
        
        try:
            # Update transaction status to completed
            await update_transaction_status(tx_id, 'completed')
            
            # Settle referral rewards
            await settle_referral_rewards(tx_id)
            
            # Mark countdown as completed
            countdown["status"] = "completed"
            
            # Call callback if provided
            if countdown.get("on_complete_callback"):
                await countdown["on_complete_callback"](tx_id)
            
            print(f"[AutoConfirm] Transaction {tx_id} auto-confirmed")
            
        except Exception as e:
            print(f"[AutoConfirm] Error auto-confirming {tx_id}: {e}")
            countdown["status"] = "error"
    
    async def cancel_countdown(self, tx_id: str):
        """
        Cancel countdown (e.g., when dispute is raised).
        """
        if tx_id in self.countdowns:
            self.countdowns[tx_id]["status"] = "cancelled"
            del self.countdowns[tx_id]
            print(f"[AutoConfirm] Countdown cancelled for {tx_id}")
    
    def get_countdown_status(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current countdown status for a transaction.
        
        Returns:
            {
                "tx_id": str,
                "time_remaining_seconds": float,
                "auto_confirm_hours": int,
                "status": str
            } or None if not found
        """
        if tx_id not in self.countdowns:
            return None
        
        countdown = self.countdowns[tx_id]
        time_remaining = (countdown["deadline"] - datetime.now()).total_seconds()
        
        return {
            "tx_id": tx_id,
            "time_remaining_seconds": max(0, time_remaining),
            "auto_confirm_hours": countdown["auto_confirm_hours"],
            "status": countdown["status"],
            "deadline": countdown["deadline"].isoformat()
        }
    
    async def initialize_pending_countdowns(self):
        """
        Initialize countdowns for pending transactions from database.
        Call this on server startup.
        """
        # TODO: Query database for pending transactions with auto_confirm settings
        # For now, this is a placeholder
        print("[AutoConfirm] Initialized pending countdowns")


# Global instance
auto_confirm_service = AutoConfirmService()
