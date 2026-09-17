"""
Inward Flow Configuration Script for InvenTree (WMS Ayusri)

Configures DB settings for:
1. Purchase Order - Receiving "new product" / create Part on the fly.
2. Part Name / IPN Duplicate Detection & Similarity Checks.
3. Barcode Generation Settings (short reference format).
4. Plugin Activation (Event hooks and Validation mixins).
"""

import os
import sys

for p in ['/home/inventree/src/backend/InvenTree', '/home/inventree/InvenTree', '/home/inventree']:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

import django
django.setup()

from common.models import InvenTreeSetting
from plugin.registry import registry

print("=== CONFIGURING INWARD FLOW SETTINGS ===")

target_settings = {
    # 1. PO Receive Settings - Allow creating Part on-the-fly & supplier parts
    'PART_CREATE_INITIAL': 'True',
    'PART_CREATE_SUPPLIER': 'True',
    'PURCHASEORDER_AUTO_COMPLETE': 'True',
    'PURCHASEORDER_MERGE_LINE_ITEMS': 'True',

    # 2. Duplicate Detection & Part Name Control
    'PART_ALLOW_DUPLICATE_NAMES': 'False',  # Prevent duplicate part names
    'PART_ALLOW_DUPLICATE_IPN': 'False',    # Prevent duplicate IPNs
    'PART_ALLOW_EDIT_IPN': 'True',

    # 3. Barcode Settings - Short reference format
    'BARCODE_ENABLE': 'True',
    'BARCODE_GENERATION_PLUGIN': 'inventreebarcode',
    'BARCODE_SHOW_TEXT': 'True',
    'BARCODE_STORE_RESULTS': 'False',

    # 4. Enable Plugin Events & Validation Hooks
    'ENABLE_PLUGINS_EVENTS': 'True',
    'ENABLE_PLUGINS_SCHEDULE': 'True',
}

for key, value in target_settings.items():
    try:
        InvenTreeSetting.set_setting(key, value, change_user=None)
        print(f"  [SET] {key} = {value}")
    except Exception as e:
        # Fallback to direct DB update
        setting, _ = InvenTreeSetting.objects.get_or_create(key=key)
        setting.value = value
        setting.save()
        print(f"  [DB] {key} = {value} (via direct save)")

print("\n=== RELOADING PLUGIN REGISTRY ===")
try:
    registry.reload_plugins()
    print("Plugin registry reloaded successfully.")
    installed = registry.plugins
    print(f"Active plugins ({len(installed)}):", list(installed.keys()))
except Exception as e:
    print("Plugin reload notification:", e)

print("\n=== CONFIGURATION COMPLETE ===")
