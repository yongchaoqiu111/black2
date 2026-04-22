"""
Redis Queue configuration for settlement tasks.
"""
import redis
from rq import Queue

# Redis connection (adjust host/port if needed)
redis_conn = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Settlement queue
settlement_queue = Queue('settlement', connection=redis_conn)

def test_redis():
    """Test Redis connection"""
    try:
        redis_conn.ping()
        print("✓ Redis connected successfully")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

if __name__ == '__main__':
    test_redis()
