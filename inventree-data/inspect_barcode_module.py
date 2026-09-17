import os
import sys

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

import sys
for name, mod in list(sys.modules.items()):
    if 'barcode' in name:
        print("  Module:", name)

try:
    import barcode
    print("  Imported 'barcode':", dir(barcode))
except Exception as e:
    print("  Failed 'import barcode':", e)

try:
    from barcode import plugins
    print("  Imported 'barcode.plugins'")
except Exception as e:
    print("  Failed 'barcode.plugins':", e)

# Check StockItem methods related to barcode
from stock.models import StockItem
item = StockItem()
print("StockItem barcode methods:", [m for m in dir(item) if 'barcode' in m])

from part.models import Part
part = Part()
print("Part barcode methods:", [m for m in dir(part) if 'barcode' in m])
