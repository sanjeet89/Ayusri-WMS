-- 1. Table Counts Summary
SELECT '--- TABLE COUNTS ---' as section;
SELECT 'part_partcategory' AS table_name, COUNT(*) FROM part_partcategory
UNION ALL SELECT 'part_part', COUNT(*) FROM part_part
UNION ALL SELECT 'company_company', COUNT(*) FROM company_company
UNION ALL SELECT 'company_supplierpart', COUNT(*) FROM company_supplierpart
UNION ALL SELECT 'company_manufacturerpart', COUNT(*) FROM company_manufacturerpart
UNION ALL SELECT 'stock_stocklocation', COUNT(*) FROM stock_stocklocation
UNION ALL SELECT 'stock_stockitem', COUNT(*) FROM stock_stockitem;

-- 2. Part Categories Structure
SELECT '--- PART CATEGORIES ---' as section;
SELECT id, name, pathstring, description FROM part_partcategory ORDER BY id LIMIT 25;

-- 3. Sample Products / Parts (~20)
SELECT '--- SAMPLE PARTS (PRODUCTS) ---' as section;
SELECT id, IPN, name, description, assembly, component, purchaseable, salable, active, units, keywords
FROM part_part ORDER BY id LIMIT 25;

-- 4. Sample Companies / Vendors (~20)
SELECT '--- SAMPLE COMPANIES (VENDORS/MANUFACTURERS) ---' as section;
SELECT id, name, description, is_supplier, is_manufacturer, is_customer, website, email
FROM company_company ORDER BY id LIMIT 25;

-- 5. Supplier Parts Mapping (~20)
SELECT '--- SUPPLIER PARTS MAPPING ---' as section;
SELECT sp.id, p.name as part_name, p.IPN as part_ipn, c.name as supplier_name, sp.SKU, sp.link
FROM company_supplierpart sp
JOIN part_part p ON sp.part_id = p.id
JOIN company_company c ON sp.supplier_id = c.id
ORDER BY sp.id LIMIT 25;

-- 6. Manufacturer Parts Mapping (~20)
SELECT '--- MANUFACTURER PARTS MAPPING ---' as section;
SELECT mp.id, p.name as part_name, c.name as manufacturer_name, mp.MPN, mp.description
FROM company_manufacturerpart mp
JOIN part_part p ON mp.part_id = p.id
JOIN company_company c ON mp.manufacturer_id = c.id
ORDER BY mp.id LIMIT 25;

-- 7. Stock Locations & Stock Items (~20)
SELECT '--- STOCK LOCATIONS ---' as section;
SELECT id, name, pathstring, description FROM stock_stocklocation ORDER BY id LIMIT 25;

SELECT '--- STOCK ITEMS ---' as section;
SELECT si.id, p.name as part_name, si.quantity, sl.pathstring as location_path, si.batch, si.serial
FROM stock_stockitem si
LEFT JOIN part_part p ON si.part_id = p.id
LEFT JOIN stock_stocklocation sl ON si.location_id = sl.id
ORDER BY si.id LIMIT 25;
