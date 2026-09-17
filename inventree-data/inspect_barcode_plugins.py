import os
import sys

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

import plugin.builtin.barcodes.inventree_barcode as ib
print("inventree_barcode dir:", [x for x in dir(ib) if not x.startswith('_')])

from plugin.registry import registry
print("Registered barcode plugins:", [p.slug for p in registry.with_mixin('barcode')])
for p in registry.with_mixin('barcode'):
    print("  Plugin:", p.slug, type(p))
    if hasattr(p, 'scan'):
        print("   has scan method")
