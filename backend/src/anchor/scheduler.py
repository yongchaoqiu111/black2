"""
Anchor Scheduler Module

Provides periodic anchoring of transaction root hashes.
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AnchorScheduler:
    def __init__(self, anchor_service, interval_hours: int = 1):
        self.anchor_service = anchor_service
        self.interval_hours = interval_hours
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def _log_anchor_result(self, result: dict):
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "anchor.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        log_entry = (
            f"[{datetime.now(timezone.utc).isoformat()}] "
            f"Anchor completed: root_hash={result['root_hash']}, "
            f"tx_count={result['transaction_count']}, "
            f"gist_url={result['gist_url']}\n"
        )

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

        logger.info(f"Anchor completed: {result['root_hash']}")

    async def _anchor_loop(self):
        while self._running:
            try:
                result = await self.anchor_service.perform_anchor()
                if result:
                    await self._log_anchor_result(result)
                else:
                    logger.info("No unanchored transactions found")
            except Exception as e:
                logger.error(f"Anchor failed: {e}")

            # Micro-transaction optimization: default to 5 minutes (300s) if interval is 0 or too small
            sleep_time = max(300, self.interval_hours * 3600)
            await asyncio.sleep(sleep_time)

    def start(self):
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._anchor_loop())
        logger.info(f"Anchor scheduler started (interval: {self.interval_hours}h)")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Anchor scheduler stopped")

    async def trigger_now(self) -> dict:
        result = await self.anchor_service.perform_anchor()
        if result:
            await self._log_anchor_result(result)
        return result or {"message": "No unanchored transactions"}