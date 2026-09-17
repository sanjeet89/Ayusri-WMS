import os
import sys

print("Step 1: Setting sys.path...", flush=True)
for p in ['/home/inventree/src/backend/InvenTree', '/var/www/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

print("Step 2: Setup Django...", flush=True)
import django
django.setup()

print("Step 3: Importing StockLocation...", flush=True)
from stock.models import StockLocation

try:
    print("Step 4: Level 1 - Building...", flush=True)
    wh, created = StockLocation.objects.get_or_create(
        name="Ayusri Main Warehouse",
        defaults={
            "description": "Central Warehouse Facility",
            "structural": True,
            "parent": None
        }
    )
    print(f"WH Level 1 created: {created}, id: {wh.pk}", flush=True)

    print("Step 5: Level 2 - Zone...", flush=True)
    zone, created = StockLocation.objects.get_or_create(
        name="Raw Materials Zone",
        parent=wh,
        defaults={
            "description": "Raw Materials & Ingredients",
            "structural": True
        }
    )
    print(f"Zone Level 2 created: {created}, id: {zone.pk}", flush=True)

    print("Step 6: Level 3 - Rack...", flush=True)
    rack, created = StockLocation.objects.get_or_create(
        name="Rack A",
        parent=zone,
        defaults={
            "description": "Heavy Duty Pallet Racking A",
            "structural": True
        }
    )
    print(f"Rack Level 3 created: {created}, id: {rack.pk}", flush=True)

    print("Step 7: Level 4 - Shelf...", flush=True)
    shelf, created = StockLocation.objects.get_or_create(
        name="Shelf 02",
        parent=rack,
        defaults={
            "description": "Level 2 Shelf",
            "structural": True
        }
    )
    print(f"Shelf Level 4 created: {created}, id: {shelf.pk}", flush=True)

    print("Step 8: Level 5 - Bin...", flush=True)
    bin_item, created = StockLocation.objects.get_or_create(
        name="Bin B-04",
        parent=shelf,
        defaults={
            "description": "Storage Bin B-04",
            "structural": False
        }
    )
    print(f"Bin Level 5 created: {created}, id: {bin_item.pk}", flush=True)

    print("Step 9: Fetching location pathstring...", flush=True)
    path = getattr(bin_item, 'pathstring', None)
    if path is None:
        path = bin_item.pathstring
    print("Generated location path:", path, flush=True)

except Exception as e:
    import traceback
    print("ERROR OCCURRED:", e, flush=True)
    traceback.print_exc()
