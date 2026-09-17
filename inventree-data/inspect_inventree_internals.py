import os
import sys

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

from common.models import InvenTreeSetting

print("=== INVENTREE SETTINGS KEYS ===")
# Inspect setting keys from common.settings module or InvenTreeSetting methods
try:
    import common.models as cm
    print("InvenTreeSetting methods/attributes:", [x for x in dir(InvenTreeSetting) if 'setting' in x.lower() or 'get' in x.lower()])
    
    # Try fetching setting keys from common.settings or InvenTreeSetting
    from InvenTree.config import get_setting
    print("Setting config imported successfully")
except Exception as e:
    print("Error inspecting settings:", e)

# Print all settings currently in DB
print("\n--- Current DB Settings ---")
for s in InvenTreeSetting.objects.all():
    print(f"  {s.key} = {s.value}")

# Check StockStatus available codes
from InvenTree.status_codes import StockStatus
print("\n=== STOCK STATUS AVAILABLE CODES ===")
print("AVAILABLE_CODES:", getattr(StockStatus, 'AVAILABLE_CODES', 'N/A'))
