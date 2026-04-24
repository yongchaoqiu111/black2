import sys
import os

print("Current directory:", os.getcwd())
print("Adding 'src' to path...")
sys.path.insert(0, 'src')

try:
    print("\n1. Testing anchor module imports...")
    from src.anchor import github_anchor
    print("   ✅ github_anchor imported")
    
    from src.anchor import x402_anchor
    print("   ✅ x402_anchor imported")
    
    from src.anchor import arbitration_timer_service
    print("   ✅ arbitration_timer_service imported")
    
    print("\n2. Testing db module imports...")
    from src.db import TransactionDB
    print("   ✅ TransactionDB imported")
    
    print("\n3. Testing utils module imports...")
    from src.utils import task_processor
    print("   ✅ task_processor imported")
    
    print("\n4. Testing x402 module imports...")
    from src.x402 import x402_bridge
    print("   ✅ x402_bridge imported")
    
    print("\n" + "="*60)
    print("🎉 ALL MODULES IMPORTED SUCCESSFULLY!")
    print("="*60)
    
except Exception as e:
    print("\n" + "="*60)
    print(f"❌ ERROR: {str(e)}")
    print("="*60)
    import traceback
    print("\nStack trace:")
    print(traceback.format_exc())
