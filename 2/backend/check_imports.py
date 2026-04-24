"""
Simple Startup Test Script

Tests if all modules can be imported correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing Black2 X402 Integration module imports...")

try:
    from anchor.github_anchor import github_anchor
    print("✅ GitHub Anchor imported")
except Exception as e:
    print(f"❌ GitHub Anchor import failed: {e}")

try:
    from anchor.x402_anchor import x402_anchor
    print("✅ X402 Anchor imported")
except Exception as e:
    print(f"❌ X402 Anchor import failed: {e}")

try:
    from anchor.dual_anchor import DualAnchorService
    print("✅ Dual Anchor imported")
except Exception as e:
    print(f"❌ Dual Anchor import failed: {e}")

try:
    from db.transaction_db import TransactionDB
    print("✅ Database module imported")
except Exception as e:
    print(f"❌ Database module import failed: {e}")

try:
    from utils.async_task_processor import task_processor
    print("✅ Async Task Processor imported")
except Exception as e:
    print(f"❌ Async Task Processor import failed: {e}")

print("\nAll imports complete!")