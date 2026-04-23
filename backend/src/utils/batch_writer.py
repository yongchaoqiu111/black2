"""
Async Batch Writer for high-concurrency scenarios.
Implements the 'Buffer & Flush' pattern to reduce DB I/O pressure.
"""
import asyncio
import aiosqlite
from collections import deque
from typing import List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class AsyncBatchWriter:
    def __init__(self, db_path: str = 'black2.db', batch_size: int = 50, flush_interval: float = 1.0):
        self.db_path = db_path
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer: deque = deque()
        self.is_running = False
        self.task = None
        self.lock = asyncio.Lock()

    async def start(self):
        """启动后台刷新任务"""
        self.is_running = True
        self.task = asyncio.create_task(self._flush_loop())
        logger.info(f"[BatchWriter] Started with batch_size={self.batch_size}, interval={self.flush_interval}s")

    async def stop(self):
        """停止并强制刷新剩余数据"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        # 最后一次强制刷新
        if self.buffer:
            await self._flush_batch(list(self.buffer))
            self.buffer.clear()
        logger.info("[BatchWriter] Stopped and flushed.")

    async def add(self, sql: str, params: Tuple):
        """添加一条待写入数据 (SQL + Params)"""
        async with self.lock:
            self.buffer.append((sql, params))
            # 如果缓冲区满了，立即触发一次异步刷新（不阻塞当前请求）
            if len(self.buffer) >= self.batch_size:
                asyncio.create_task(self._force_flush())

    async def _force_flush(self):
        """强制刷新当前缓冲区"""
        async with self.lock:
            if not self.buffer:
                return
            batch = list(self.buffer)
            self.buffer.clear()
        await self._execute_batch(batch)

    async def _flush_loop(self):
        """定时刷新循环"""
        while self.is_running:
            await asyncio.sleep(self.flush_interval)
            await self._force_flush()

    async def _execute_batch(self, batch: List[Tuple[str, Tuple]]):
        """执行实际的数据库批量写入"""
        if not batch:
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for sql, params in batch:
                    await db.execute(sql, params)
                await db.commit()
            logger.debug(f"[BatchWriter] Successfully flushed {len(batch)} records.")
        except Exception as e:
            logger.error(f"[BatchWriter] Failed to flush batch: {e}")
            # 生产环境建议：将失败的批次写入本地文件以便后续重试

# 全局实例：用于非核心路径的异步写入
log_writer = AsyncBatchWriter(batch_size=100, flush_interval=2.0)
referral_writer = AsyncBatchWriter(batch_size=20, flush_interval=0.5)
