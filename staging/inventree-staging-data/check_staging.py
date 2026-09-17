import os
import sys
import json

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

from part.models import Part, PartCategory, PartParameter
from company.models import Company, SupplierPart, ManufacturerPart
from stock.models import StockLocation, StockItem
from build.models import Build
from order.models import PurchaseOrder, SalesOrder

data = {}

data["counts"] = {
    "PartCategory": PartCategory.objects.count(),
    "Part": Part.objects.count(),
    "Company": Company.objects.count(),
    "SupplierPart": SupplierPart.objects.count(),
    "ManufacturerPart": ManufacturerPart.objects.count(),
    "StockLocation": StockLocation.objects.count(),
    "StockItem": StockItem.objects.count(),
    "Build": Build.objects.count(),
    "PurchaseOrder": PurchaseOrder.objects.count(),
    "SalesOrder": SalesOrder.objects.count(),
}

# Categories
categories = []
for cat in PartCategory.objects.all():
    categories.append({
        "id": cat.pk,
        "name": cat.name,
        "path": cat.pathstring,
        "description": cat.description,
        "parent": cat.parent.name if cat.parent else None,
        "parts_count": cat.parts.count()
    })
data["categories"] = categories

# Parts sample (~20)
parts_sample = []
for p in Part.objects.all()[:25]:
    suppliers = []
    for sp in SupplierPart.objects.filter(part=p):
        suppliers.append({
            "supplier_name": sp.supplier.name,
            "SKU": sp.SKU,
            "manufacturer_name": sp.manufacturer_part.manufacturer.name if sp.manufacturer_part and sp.manufacturer_part.manufacturer else None,
            "MPN": sp.manufacturer_part.MPN if sp.manufacturer_part else None,
        })
    
    params = {}
    for par in PartParameter.objects.filter(part=p):
        params[par.template.name] = par.data

    parts_sample.append({
        "id": p.pk,
        "IPN": p.IPN,
        "name": p.name,
        "description": p.description,
        "category_id": p.category.pk if p.category else None,
        "category_path": p.category.pathstring if p.category else None,
        "is_assembly": p.assembly,
        "is_component": p.component,
        "is_purchaseable": p.purchaseable,
        "is_salable": p.salable,
        "is_virtual": p.virtual,
        "is_active": p.active,
        "units": p.units,
        "keywords": p.keywords,
        "suppliers": suppliers,
        "parameters": params
    })
data["parts_sample"] = parts_sample

# Companies sample (all/up to 25)
companies_sample = []
for c in Company.objects.all()[:25]:
    supplier_parts_count = SupplierPart.objects.filter(supplier=c).count()
    mfg_parts_count = ManufacturerPart.objects.filter(manufacturer=c).count()
    companies_sample.append({
        "id": c.pk,
        "name": c.name,
        "description": c.description,
        "is_supplier": c.is_supplier,
        "is_manufacturer": c.is_manufacturer,
        "is_customer": c.is_customer,
        "website": c.website,
        "phone": c.phone,
        "email": c.email,
        "supplier_parts_count": supplier_parts_count,
        "manufacturer_parts_count": mfg_parts_count
    })
data["companies_sample"] = companies_sample

# Supplier Parts sample (~20)
supplier_parts_sample = []
for sp in SupplierPart.objects.all()[:25]:
    supplier_parts_sample.append({
        "id": sp.pk,
        "part_id": sp.part.pk,
        "part_name": sp.part.name,
        "part_IPN": sp.part.IPN,
        "supplier_name": sp.supplier.name,
        "SKU": sp.SKU,
        "manufacturer_name": sp.manufacturer_part.manufacturer.name if sp.manufacturer_part and sp.manufacturer_part.manufacturer else None,
        "MPN": sp.manufacturer_part.MPN if sp.manufacturer_part else None,
        "link": sp.link,
        "note": sp.note
    })
data["supplier_parts_sample"] = supplier_parts_sample

# Manufacturer Parts sample (~20)
manufacturer_parts_sample = []
for mp in ManufacturerPart.objects.all()[:25]:
    manufacturer_parts_sample.append({
        "id": mp.pk,
        "part_id": mp.part.pk,
        "part_name": mp.part.name,
        "manufacturer_name": mp.manufacturer.name,
        "MPN": mp.MPN,
        "description": mp.description,
    })
data["manufacturer_parts_sample"] = manufacturer_parts_sample

# Stock Locations & Items sample
stock_locations = []
for loc in StockLocation.objects.all():
    stock_locations.append({
        "id": loc.pk,
        "name": loc.name,
        "path": loc.pathstring,
        "description": loc.description,
        "items_count": loc.items.count()
    })
data["stock_locations"] = stock_locations

stock_items_sample = []
for si in StockItem.objects.all()[:25]:
    stock_items_sample.append({
        "id": si.pk,
        "part_name": si.part.name if si.part else None,
        "quantity": float(si.quantity),
        "location": si.location.pathstring if si.location else None,
        "status": si.status,
        "serial": si.serial,
        "batch": si.batch
    })
data["stock_items_sample"] = stock_items_sample

output_path = '/home/inventree/data/staging_data_report.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Successfully generated report at {output_path}!")
