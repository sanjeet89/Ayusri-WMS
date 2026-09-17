import os
import sys

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

from common.models import InvenTreeSetting
from plugin import InvenTreePlugin
import plugin.mixins as mixins
from stock.models import StockItem
from InvenTree.status_codes import StockStatus

print("=== INVENTREE PLUGIN MIXINS ===")
for m in dir(mixins):
    if 'Mixin' in m or 'Plugin' in m:
        print(" -", m)

print("\n=== STOCK STATUS CODES ===")
for code in StockStatus.CODES:
    print(f"  {code}: {StockStatus.label(code)} (key: {StockStatus.value(code)})")

print("\n=== RELEVANT INVENTREE SETTINGS IN DB ===")
all_settings = InvenTreeSetting.objects.all()
for s in all_settings:
    if any(k in s.key.upper() for k in ['PO', 'PURCHASE', 'PART', 'SIMILAR', 'BARCODE', 'RECEIVE', 'DUPLICATE']):
        print(f"  {s.key} = {s.value}")

print("\n=== INVENTREE SETTING KEYS DEFINED IN BACKEND ===")
try:
    from common.settings import INVENTREE_SETTINGS
    for key, spec in INVENTREE_SETTINGS.items():
        if any(k in key.upper() for k in ['PO', 'PURCHASE', 'PART', 'SIMILAR', 'BARCODE', 'RECEIVE', 'DUPLICATE']):
            print(f"  [DEF] {key}: default={spec.get('default')}, description={str(spec.get('description', ''))[:60]}")
except Exception as e:
    print("Could not load default settings dict:", e)
