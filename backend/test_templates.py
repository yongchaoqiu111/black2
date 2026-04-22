import sys
import traceback

try:
    print("Starting import...")
    from src.contract.templates import list_templates
    print("Import successful!")
    
    templates = list_templates()
    print(f"Found {len(templates)} templates:")
    for t in templates:
        print(f"  - {t}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)
