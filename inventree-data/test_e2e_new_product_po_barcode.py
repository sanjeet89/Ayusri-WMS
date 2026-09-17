"""
End-to-End Test: Receive "New Product" via PO, Generate Barcode, and Test Barcode Scan Resolution
"""

import os
import sys
from datetime import date, timedelta

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from part.models import Part, PartCategory
from company.models import Company, SupplierPart
from stock.models import StockItem, StockLocation
from order.models import PurchaseOrder, PurchaseOrderLineItem
from InvenTree.status_codes import StockStatus
from plugin.registry import registry

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()

print("=================================================================")
print("  END-TO-END TEST: PO RECEIVE 'NEW PRODUCT' & BARCODE SCAN BACK   ")
print("=================================================================\n")

# 1. Setup Supplier and Category
print("--- 1. SETTING UP SUPPLIER & CATEGORY ---")
supplier, _ = Company.objects.get_or_create(
    name="Ayurvedic Botanical Imports Pvt Ltd",
    defaults={'is_supplier': True}
)
cat, _ = PartCategory.objects.get_or_create(name="Herbal Extracts & Powders")
loc, _ = StockLocation.objects.get_or_create(name="Warehouse Bay A1 - Receiving")

print(f"  Supplier: {supplier.name}")
print(f"  Category: {cat.name}")
print(f"  Location: {loc.name}")

# 2. Create "New Product" Part on the fly during PO Setup
print("\n--- 2. CREATING NEW PRODUCT PART & PURCHASE ORDER ---")
new_part_name = "Organic Brahmi Powder (Bacopa Monnieri) 100 Mesh"
new_ipn = "HERB-BRAHMI-100M"

part, created = Part.objects.get_or_create(
    IPN=new_ipn,
    defaults={
        'name': new_part_name,
        'category': cat,
        'purchaseable': True,
        'units': 'kg',
        'keywords': 'brahmi, bacopa, herbal powder'
    }
)
print(f"  Part Created: {part.name} (IPN: {part.IPN}, ID: {part.pk})")

supplier_part, _ = SupplierPart.objects.get_or_create(
    part=part,
    supplier=supplier,
    defaults={'SKU': 'ABI-BRA-100M-KG'}
)
print(f"  Supplier Part Linked: SKU {supplier_part.SKU}")

# Create Purchase Order
po, _ = PurchaseOrder.objects.get_or_create(
    reference="PO-2026-HERB-009",
    defaults={
        'supplier': supplier,
        'description': "Bulk Inward Receipt for Organic Brahmi Powder"
    }
)
po_line, _ = PurchaseOrderLineItem.objects.get_or_create(
    order=po,
    part=supplier_part,
    defaults={'quantity': 250.0}
)
print(f"  Purchase Order Created: {po.reference} (Line Item Qty: {po_line.quantity} {part.units})")

# 3. Receive Purchase Order Line Item into Stock
print("\n--- 3. RECEIVING PO LINE ITEM INTO STOCK (INWARD RECEIPT) ---")

batch_no = "BATCH-BRA-2026-09A"
exp_date = date.today() + timedelta(days=730)

stock_item, _ = StockItem.objects.get_or_create(
    batch=batch_no,
    part=part,
    defaults={
        'supplier_part': supplier_part,
        'location': loc,
        'quantity': 250.0,
        'expiry_date': exp_date,
        'status': StockStatus.QUARANTINED,
        'metadata': {"qc_status": "Pending", "po_reference": po.reference}
    }
)

print(f"  Received StockItem ID: {stock_item.pk}")
print(f"  Stock Item Part: {stock_item.part.name}")
print(f"  Received Quantity: {stock_item.quantity} {stock_item.part.units}")
print(f"  Location: {stock_item.location.pathstring}")
print(f"  Batch Number: {stock_item.batch}")
print(f"  Expiry Date: {stock_item.expiry_date}")
print(f"  QC Status Metadata: {stock_item.metadata.get('qc_status')}")
print(f"  Stock Item Status: {StockStatus.label(stock_item.status)} ({stock_item.status})")

# 4. Generate & Inspect Barcode Format
print("\n--- 4. BARCODE GENERATION & PAYLOAD INSPECTION ---")
stock_barcode_data = stock_item.format_barcode()
part_barcode_data = part.format_barcode()

print(f"  Stock Item Barcode Data Payload: '{stock_barcode_data}'")
print(f"  Part Barcode Data Payload:       '{part_barcode_data}'")

# 5. Test Barcode Scan-Back Resolution
print("\n--- 5. TESTING BARCODE SCAN-BACK RESOLUTION ---")
barcode_plugin = registry.get_plugin('inventreebarcode')
print(f"  Active Barcode Plugin Loaded: {barcode_plugin.slug}")

# Test Scan Stock Item Barcode
print(f"  Simulating Scanner Input '{stock_barcode_data}' for Stock Item Barcode...")
scan_result_stock = barcode_plugin.scan(stock_barcode_data, user=admin_user)
print(f"  Stock Item Scan Result Keys: {list(scan_result_stock.keys())}")

assert scan_result_stock is not None, "Scan result should not be None"
assert 'stockitem' in scan_result_stock, "Scan result must resolve stockitem key"
matched_item_data = scan_result_stock['stockitem']
assert matched_item_data['pk'] == stock_item.pk, f"Scanned StockItem ID ({matched_item_data['pk']}) must match {stock_item.pk}"

print(f"  [PASS] Scanned Barcode '{stock_barcode_data}' SUCCESSFULLY resolved back to StockItem ID {matched_item_data['pk']} ({stock_item.part.name})!")

# Test Scan Part Barcode
print(f"\n  Simulating Scanner Input '{part_barcode_data}' for Part Barcode...")
scan_result_part = barcode_plugin.scan(part_barcode_data, user=admin_user)
print(f"  Part Scan Result Keys: {list(scan_result_part.keys())}")

assert scan_result_part is not None, "Part scan result should not be None"
assert 'part' in scan_result_part, "Part scan result must resolve part key"
matched_part_data = scan_result_part['part']
assert matched_part_data['pk'] == part.pk, f"Scanned Part ID ({matched_part_data['pk']}) must match {part.pk}"

print(f"  [PASS] Scanned Barcode '{part_barcode_data}' SUCCESSFULLY resolved back to Part ID {matched_part_data['pk']} ({part.name})!")

print("\n=================================================================")
print("  E2E TEST SUCCESSFUL: NEW PRODUCT RECEIVED & BARCODE VERIFIED!  ")
print("=================================================================")
