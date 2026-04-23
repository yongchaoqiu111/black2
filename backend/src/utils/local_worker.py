"""
Local Settlement Listener for Windows.
Uses threading to process RQ jobs since os.fork is not available on Windows.
"""
import time
import threading
from rq import Worker, Queue
from src.utils.redis_queue import redis_conn, settlement_queue

def start_listener():
    """Start a background thread to listen for settlement jobs."""
    def _run_worker():
        print("[Worker] Starting local settlement listener...")
        try:
            # Use simple worker that doesn't require fork
            worker = Worker([settlement_queue], connection=redis_conn)
            worker.work(with_scheduler=False)
        except Exception as e:
            print(f"[Worker] Error: {e}")

    thread = threading.Thread(target=_run_worker, daemon=True)
    thread.start()
    print("[Worker] Listener thread started.")

if __name__ == '__main__':
    start_listener()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Worker] Stopping listener...")
