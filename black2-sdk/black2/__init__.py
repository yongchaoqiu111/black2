"""
Black2 SDK - Core Package Initialization
"""

from .reputation import ReputationEngine
from .storage import StorageAdapter
from .x402_bridge import X402Bridge, X402Error, X402ErrorCode
from .privacy import PrivacyManager, AnonymousIdentity, PrivacyLevel
from .client import B2PClient

__version__ = "1.0.0"
__all__ = [
    "ReputationEngine",
    "StorageAdapter",
    "X402Bridge",
    "X402Error",
    "X402ErrorCode",
    "PrivacyManager",
    "AnonymousIdentity",
    "PrivacyLevel",
    "B2PClient",
]
