import os
import sys

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

from part.models import Part, PartCategory
from company.models import Company, SupplierPart, ManufacturerPart
from stock.models import StockLocation, StockItem

print("=== INVENTREE STAGING CURRENT DATA STATUS ===")
print("Part Categories:", PartCategory.objects.count())
print("Parts:", Part.objects.count())
print("Companies:", Company.objects.count())
print("Supplier Parts:", SupplierPart.objects.count())
print("Manufacturer Parts:", ManufacturerPart.objects.count())
print("Stock Locations:", StockLocation.objects.count())
print("Stock Items:", StockItem.objects.count())

print("\n--- Categories List ---")
for cat in PartCategory.objects.all()[:20]:
    print(f"ID: {cat.pk} | Path: {cat.pathstring} | Name: {cat.name}")

print("\n--- Sample Parts (first 20) ---")
for p in Part.objects.all()[:20]:
    print(f"ID: {p.pk} | IPN: {p.IPN} | Name: {p.name} | Category: {p.category.name if p.category else 'None'}")

print("\n--- Sample Companies (first 20) ---")
for c in Company.objects.all()[:20]:
    print(f"ID: {c.pk} | Name: {c.name} | Supplier: {c.is_supplier} | Manufacturer: {c.is_manufacturer}")
