"""
Rate Limiter - Prevent API abuse
"""
import time
from typing import Dict, Tuple


class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, float] = {}  # key -> last_request_time
    
    def is_allowed(self, key: str, interval: int = 60) -> Tuple[bool, int]:
        """
        Check if request is allowed
        
        Args:
            key: Unique identifier (e.g., user_id, ip_address)
            interval: Time interval in seconds (default: 60)
            
        Returns:
            Tuple[bool, int]: (is_allowed, remaining_seconds)
        """
        now = time.time()
        
        if key not in self.requests:
            # First request
            self.requests[key] = now
            return True, 0
        
        last_request = self.requests[key]
        elapsed = now - last_request
        
        if elapsed >= interval:
            # Allowed, update timestamp
            self.requests[key] = now
            return True, 0
        else:
            # Not allowed
            remaining = max(0, int(interval - elapsed + 0.99)) # Round up and ensure non-negative
            if remaining == 0:
                # Edge case: time passed but integer conversion showed 0
                self.requests[key] = now
                return True, 0
            return False, remaining
    
    def cleanup(self, max_age: int = 3600):
        """Remove old entries to prevent memory leak"""
        now = time.time()
        expired_keys = [
            key for key, timestamp in self.requests.items()
            if now - timestamp > max_age
        ]
        for key in expired_keys:
            del self.requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()
