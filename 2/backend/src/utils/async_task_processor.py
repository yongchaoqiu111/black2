"""
Async Task Processor

Handles background tasks for X402 on-chain anchoring to avoid blocking API responses.
Following Black2 Protocol for high availability and performance.
"""

import asyncio
import logging
from collections import deque
from typing import Callable, Optional, Any, Dict, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AsyncTaskProcessor:
    def __init__(self, max_workers: int = 3, max_queue_size: int = 1000):
        self.task_queue = deque()
        self.workers = []
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.running = False
        self._processed_count = 0
        self._failed_count = 0

    async def start(self):
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop(i))
            self.workers.append(worker)
            logger.info(f"Worker {i} started")

    async def stop(self):
        if not self.running:
            return
        
        self.running = False
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
        logger.info(f"AsyncTaskProcessor stopped. Processed: {self._processed_count}, Failed: {self._failed_count}")

    async def submit_task(self, task_func: Callable, *args, **kwargs) -> Optional[asyncio.Task]:
        if len(self.task_queue) >= self.max_queue_size:
            logger.warning(f"Queue full ({self.max_queue_size}), task rejected")
            return None
        
        task_id = kwargs.pop('task_id', f"task_{datetime.now(timezone.utc).isoformat()}")
        self.task_queue.append({
            'id': task_id,
            'func': task_func,
            'args': args,
            'kwargs': kwargs,
            'submitted_at': datetime.now(timezone.utc),
            'retry_count': 0,
            'max_retries': kwargs.pop('max_retries', 3)
        })
        
        logger.debug(f"Task {task_id} submitted")
        return asyncio.create_task(self._wait_for_task_result(task_id))

    async def _worker_loop(self, worker_id: int):
        while self.running or len(self.task_queue) > 0:
            try:
                task_data = None
                
                if self.task_queue:
                    task_data = self.task_queue.popleft()
                
                if task_data:
                    await self._execute_task(task_data, worker_id)
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def _execute_task(self, task_data: Dict, worker_id: int):
        task_id = task_data['id']
        
        try:
            result = await task_data['func'](*task_data['args'], **task_data['kwargs'])
            self._processed_count += 1
            logger.debug(f"Worker {worker_id} completed task {task_id}")
            return result
        except Exception as e:
            logger.error(f"Worker {worker_id} failed task {task_id}: {e}", exc_info=True)
            task_data['retry_count'] += 1
            
            if task_data['retry_count'] <= task_data['max_retries']:
                delay = min(2 ** task_data['retry_count'], 30)
                logger.warning(f"Retrying task {task_id} (attempt {task_data['retry_count']}/{task_data['max_retries']}) in {delay}s")
                await asyncio.sleep(delay)
                self.task_queue.append(task_data)
            else:
                self._failed_count += 1
                logger.error(f"Max retries reached for task {task_id}")

    async def _wait_for_task_result(self, task_id: str):
        logger.debug(f"Waiting for task {task_id} result (best effort)")
        return {'task_id': task_id, 'submitted': True}

    def get_queue_size(self) -> int:
        return len(self.task_queue)

    def get_stats(self) -> Dict:
        return {
            'queue_size': len(self.task_queue),
            'processed_count': self._processed_count,
            'failed_count': self._failed_count,
            'workers_count': len(self.workers),
            'is_running': self.running
        }


class X402BatchProcessor:
    def __init__(self, async_processor: AsyncTaskProcessor, x402_anchor, batch_size: int = 100, batch_timeout: float = 60.0):
        self.async_processor = async_processor
        self.x402_anchor = x402_anchor
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._pending_items = []
        self._last_batch_time = datetime.now(timezone.utc)
        self._batch_task = None

    async def start(self):
        self._batch_task = asyncio.create_task(self._batch_processor_loop())

    async def stop(self):
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
        await self._flush_batch()

    async def add_to_batch(self, commit_hash: str, anchor_type: str, metadata: Optional[Dict] = None):
        self._pending_items.append({
            'commit_hash': commit_hash,
            'anchor_type': anchor_type,
            'metadata': metadata
        })
        
        if len(self._pending_items) >= self.batch_size:
            await self._flush_batch()

    async def _batch_processor_loop(self):
        while True:
            try:
                await asyncio.sleep(5)
                time_since_last = (datetime.now(timezone.utc) - self._last_batch_time).total_seconds()
                
                if time_since_last >= self.batch_timeout and len(self._pending_items) > 0:
                    await self._flush_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batch processor loop error: {e}", exc_info=True)

    async def _flush_batch(self):
        if not self._pending_items:
            return
        
        items = self._pending_items.copy()
        self._pending_items = []
        self._last_batch_time = datetime.now(timezone.utc)
        
        await self.async_processor.submit_task(
            self._process_batch,
            items
        )

    async def _process_batch(self, items: List[Dict]):
        if not items:
            return
        
        commit_hashes = [item['commit_hash'] for item in items]
        result = await self.x402_anchor.batch_anchor(commit_hashes, 'arbitration')
        
        if result.get('success'):
            logger.info(f"Batch of {len(items)} anchors processed: {result.get('tx_hash')}")
        else:
            logger.error(f"Batch processing failed: {result.get('error')}")


task_processor = AsyncTaskProcessor()
batch_processor = None