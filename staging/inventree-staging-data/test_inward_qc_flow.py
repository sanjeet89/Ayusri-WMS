"""
Integration Test Script for Inward Flow & QC Inspection Plugin (WMS Ayusri Staging)
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

from part.models import Part, PartCategory
from stock.models import StockItem, StockLocation
from company.models import Company, SupplierPart
from order.models import PurchaseOrder, PurchaseOrderLineItem
from InvenTree.status_codes import StockStatus
from common.models import InvenTreeSetting
from django.core.exceptions import ValidationError
from plugins.qc_inspection_plugin import QCInspectionPlugin

print("=========================================================")
print("      INWARD FLOW & QC INSPECTION PLUGIN INTEGRATION TEST ")
print("=========================================================\n")

# 1. Verify DB Settings
print("--- 1. VERIFYING SYSTEM SETTINGS ---")
settings_checks = [
    ('PART_ALLOW_DUPLICATE_NAMES', 'False'),
    ('PART_ALLOW_DUPLICATE_IPN', 'False'),
    ('BARCODE_ENABLE', 'True'),
    ('PART_CREATE_SUPPLIER', 'True'),
]
for key, expected in settings_checks:
    val = InvenTreeSetting.get_setting(key)
    print(f"  * {key} = {val} (Expected: {expected}) -> {'PASS' if str(val) == expected else 'CHECK'}")

# 2. Setup Test Location and Part
print("\n--- 2. PREPARING TEST DATA ---")
cat, _ = PartCategory.objects.get_or_create(name="QC Test Category")
part, _ = Part.objects.get_or_create(
    name="Herbal Raw Extract - Ashwagandha Grade A",
    defaults={
        'IPN': 'HERB-ASH-001',
        'category': cat,
        'purchaseable': True,
        'units': 'kg'
    }
)
loc, _ = StockLocation.objects.get_or_create(name="Inward QC Holding Area")

print(f"  Part: {part.name} (ID: {part.pk})")
print(f"  Location: {loc.name} (ID: {loc.pk})")

# 3. Simulate Inward Stock Item Creation (PO Receipt)
print("\n--- 3. CREATING STOCK ITEM (SIMULATING PO RECEIPT) ---")
stock_item = StockItem.objects.create(
    part=part,
    location=loc,
    quantity=100.0,
    batch="BATCH-20260916-01",
    expiry_date=date.today() + timedelta(days=365),
    status=StockStatus.QUARANTINED,
    metadata={"qc_status": "Pending"}
)

print(f"  Created StockItem ID: {stock_item.pk}")
print(f"  Quantity: {stock_item.quantity} {part.units}")
print(f"  Batch: {stock_item.batch}")
print(f"  Expiry Date: {stock_item.expiry_date}")
print(f"  Initial Status: {StockStatus.label(stock_item.status)} ({stock_item.status})")
print(f"  Initial QC Metadata: {stock_item.metadata}")

assert stock_item.metadata.get('qc_status') == 'Pending', "QC Status should be Pending"
assert stock_item.status == StockStatus.QUARANTINED, "Initial status must be QUARANTINED (75)"
assert not stock_item.in_stock, "Stock should NOT be marked available while in QC"
print("  [SUCCESS] Stock item created in QUARANTINED state with qc_status='Pending'.")

# 4. Test Validation Gatekeeping (Block premature transition to OK)
print("\n--- 4. TESTING QC VALIDATION GATEKEEPING ---")
plugin = QCInspectionPlugin()
stock_item.status = StockStatus.OK
try:
    plugin.validate_stock_item(stock_item)
    print("  [FAIL] Validation should have raised ValidationError when setting status=OK with Pending QC.")
    assert False, "Expected ValidationError"
except ValidationError as ve:
    print(f"  [SUCCESS] Blocked transition to OK as expected: {ve}")

# Reset status back
stock_item.status = StockStatus.QUARANTINED
stock_item.save()

# 5. Transition QC Status to Accepted via Plugin
print("\n--- 5. ACCEPTING QC INSPECTION ---")
updated_item = QCInspectionPlugin.set_qc_status(
    stock_item_id=stock_item.pk,
    new_qc_status='Accepted',
    user_note='Inspected & Passed Lab Analysis COA #99821'
)

print(f"  Updated Status: {StockStatus.label(updated_item.status)} ({updated_item.status})")
print(f"  Updated QC Metadata: {updated_item.metadata}")
assert updated_item.metadata.get('qc_status') == 'Accepted'
assert updated_item.status == StockStatus.OK
assert updated_item.in_stock, "Stock item should now be in stock & available"
print("  [SUCCESS] QC status updated to 'Accepted', stock status changed to OK (10), stock is now AVAILABLE.")

print("\n=========================================================")
print("      ALL INWARD FLOW & QC PLUGIN TESTS PASSED!         ")
print("=========================================================")
