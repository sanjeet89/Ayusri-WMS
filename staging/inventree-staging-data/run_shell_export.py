import json

from part.models import Part, PartCategory, PartParameter
from company.models import Company, SupplierPart, ManufacturerPart
from stock.models import StockLocation, StockItem
from build.models import Build
from order.models import PurchaseOrder, SalesOrder

report = {}

# 1. Summary Counts
report["counts"] = {
    "Part Categories": PartCategory.objects.count(),
    "Parts (Products)": Part.objects.count(),
    "Companies (Vendors/Mfrs/Customers)": Company.objects.count(),
    "Supplier Parts": SupplierPart.objects.count(),
    "Manufacturer Parts": ManufacturerPart.objects.count(),
    "Stock Locations": StockLocation.objects.count(),
    "Stock Items": StockItem.objects.count(),
    "Build Orders": Build.objects.count(),
    "Purchase Orders": PurchaseOrder.objects.count(),
    "Sales Orders": SalesOrder.objects.count(),
}

# 2. Categories Structure
categories = []
for cat in PartCategory.objects.all():
    categories.append({
        "id": cat.pk,
        "name": cat.name,
        "path": cat.pathstring,
        "description": cat.description or "",
        "parent": cat.parent.name if cat.parent else None,
        "parts_count": cat.parts.count()
    })
report["categories"] = categories

# 3. Sample Products / Parts (~20-25 sample)
parts_sample = []
for p in Part.objects.all().order_by('id')[:25]:
    suppliers = []
    for sp in SupplierPart.objects.filter(part=p):
        suppliers.append({
            "supplier_name": sp.supplier.name if sp.supplier else "N/A",
            "SKU": sp.SKU,
            "manufacturer_name": sp.manufacturer_part.manufacturer.name if sp.manufacturer_part and sp.manufacturer_part.manufacturer else "N/A",
            "MPN": sp.manufacturer_part.MPN if sp.manufacturer_part else "N/A",
            "link": sp.link or ""
        })
    
    params = {}
    for par in PartParameter.objects.filter(part=p):
        params[par.template.name] = par.data

    parts_sample.append({
        "id": p.pk,
        "IPN": p.IPN or "",
        "name": p.name,
        "description": p.description or "",
        "category_id": p.category.pk if p.category else None,
        "category_path": p.category.pathstring if p.category else "Uncategorized",
        "is_assembly": p.assembly,
        "is_component": p.component,
        "is_purchaseable": p.purchaseable,
        "is_salable": p.salable,
        "is_virtual": p.virtual,
        "is_active": p.active,
        "units": p.units or "",
        "keywords": p.keywords or "",
        "suppliers": suppliers,
        "parameters": params
    })
report["parts_sample"] = parts_sample

# 4. Sample Companies / Vendors (~20-25 sample)
companies_sample = []
for c in Company.objects.all().order_by('id')[:25]:
    sp_count = SupplierPart.objects.filter(supplier=c).count()
    mp_count = ManufacturerPart.objects.filter(manufacturer=c).count()
    companies_sample.append({
        "id": c.pk,
        "name": c.name,
        "description": c.description or "",
        "is_supplier": c.is_supplier,
        "is_manufacturer": c.is_manufacturer,
        "is_customer": c.is_customer,
        "website": c.website or "",
        "phone": c.phone or "",
        "email": c.email or "",
        "supplied_parts_count": sp_count,
        "manufactured_parts_count": mp_count
    })
report["companies_sample"] = companies_sample

# 5. Supplier Parts Sample (~20-25)
supplier_parts_sample = []
for sp in SupplierPart.objects.all().order_by('id')[:25]:
    supplier_parts_sample.append({
        "id": sp.pk,
        "part_id": sp.part.pk if sp.part else None,
        "part_name": sp.part.name if sp.part else "N/A",
        "part_IPN": sp.part.IPN if sp.part else "",
        "supplier_name": sp.supplier.name if sp.supplier else "N/A",
        "SKU": sp.SKU,
        "manufacturer_name": sp.manufacturer_part.manufacturer.name if sp.manufacturer_part and sp.manufacturer_part.manufacturer else "N/A",
        "MPN": sp.manufacturer_part.MPN if sp.manufacturer_part else "N/A",
        "link": sp.link or "",
        "note": sp.note or ""
    })
report["supplier_parts_sample"] = supplier_parts_sample

# 6. Manufacturer Parts Sample (~20-25)
manufacturer_parts_sample = []
for mp in ManufacturerPart.objects.all().order_by('id')[:25]:
    manufacturer_parts_sample.append({
        "id": mp.pk,
        "part_id": mp.part.pk if mp.part else None,
        "part_name": mp.part.name if mp.part else "N/A",
        "manufacturer_name": mp.manufacturer.name if mp.manufacturer else "N/A",
        "MPN": mp.MPN,
        "description": mp.description or ""
    })
report["manufacturer_parts_sample"] = manufacturer_parts_sample

# 7. Stock Locations & Stock Items Sample
stock_locations = []
for loc in StockLocation.objects.all():
    stock_locations.append({
        "id": loc.pk,
        "name": loc.name,
        "path": loc.pathstring,
        "description": loc.description or "",
        "items_count": loc.items.count()
    })
report["stock_locations"] = stock_locations

stock_items_sample = []
for si in StockItem.objects.all().order_by('id')[:25]:
    stock_items_sample.append({
        "id": si.pk,
        "part_name": si.part.name if si.part else "N/A",
        "quantity": float(si.quantity),
        "location": si.location.pathstring if si.location else "No Location",
        "status": si.status,
        "batch": si.batch or "",
        "serial": si.serial or ""
    })
report["stock_items_sample"] = stock_items_sample

# Save JSON report
json_out = '/home/inventree/data/master_data_report.json'
with open(json_out, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

# Save human-readable TXT summary
txt_out = '/home/inventree/data/master_data_summary.txt'
with open(txt_out, 'w', encoding='utf-8') as f:
    f.write("=====================================================\n")
    f.write("      INVENTREE STAGING MASTER DATA REPORT           \n")
    f.write("=====================================================\n\n")
    
    f.write("--- 1. MASTER DATA RECORD COUNTS ---\n")
    for k, v in report["counts"].items():
        f.write(f"  * {k}: {v}\n")
    f.write("\n")

    f.write("--- 2. CATEGORIES STRUCTURE ---\n")
    for cat in categories:
        f.write(f"  [ID {cat['id']}] {cat['path']} ({cat['parts_count']} parts)\n")
    f.write("\n")

    f.write(f"--- 3. SAMPLE PRODUCTS / PARTS ({len(parts_sample)} items) ---\n")
    for p in parts_sample:
        f.write(f"  - ID: {p['id']} | IPN: '{p['IPN']}' | Name: {p['name']}\n")
        f.write(f"    Category: {p['category_path']} | Assembly: {p['is_assembly']} | Component: {p['is_component']}\n")
        f.write(f"    Purchaseable: {p['is_purchaseable']} | Salable: {p['is_salable']} | Units: {p['units']}\n")
        if p['parameters']:
            f.write(f"    Parameters: {p['parameters']}\n")
        if p['suppliers']:
            f.write(f"    Suppliers: {len(p['suppliers'])} linked\n")
            for sp in p['suppliers']:
                f.write(f"      * Supplier: {sp['supplier_name']} | SKU: {sp['SKU']} | Mfr: {sp['manufacturer_name']} | MPN: {sp['MPN']}\n")
        f.write("\n")

    f.write(f"--- 4. SAMPLE VENDORS / COMPANIES ({len(companies_sample)} items) ---\n")
    for c in companies_sample:
        types = []
        if c['is_supplier']: types.append("Supplier")
        if c['is_manufacturer']: types.append("Manufacturer")
        if c['is_customer']: types.append("Customer")
        f.write(f"  - ID: {c['id']} | Name: {c['name']} | Role(s): {', '.join(types)}\n")
        f.write(f"    Supplied Parts Count: {c['supplied_parts_count']} | Manufactured Parts Count: {c['manufactured_parts_count']}\n")
        if c['website']: f.write(f"    Website: {c['website']}\n")
        f.write("\n")

    f.write(f"--- 5. SAMPLE SUPPLIER PARTS ({len(supplier_parts_sample)} items) ---\n")
    for sp in supplier_parts_sample[:15]:
        f.write(f"  - ID: {sp['id']} | Part: {sp['part_name']} (IPN: {sp['part_IPN']}) | Supplier: {sp['supplier_name']} | SKU: {sp['SKU']}\n")
        if sp['MPN'] != "N/A":
            f.write(f"    Mfr: {sp['manufacturer_name']} | MPN: {sp['MPN']}\n")
    f.write("\n")

    f.write(f"--- 6. STOCK LOCATIONS & ITEMS ---\n")
    for loc in stock_locations:
        f.write(f"  [Location ID {loc['id']}] {loc['path']} ({loc['items_count']} items)\n")
    f.write(f"  Sample Stock Items ({len(stock_items_sample)} items):\n")
    for si in stock_items_sample[:15]:
        f.write(f"    * Stock ID {si['id']} | Part: {si['part_name']} | Qty: {si['quantity']} | Location: {si['location']}\n")
    f.write("\n")

print("SUCCESS: Django shell script complete!")
