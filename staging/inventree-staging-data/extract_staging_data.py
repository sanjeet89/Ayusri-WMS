import psycopg2
import psycopg2.extras
import json
import sys

print("Connecting to Postgres on 127.0.0.1:5433 (sslmode=disable)...", flush=True)

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5433,
        dbname="inventree_staging",
        user="pguser_staging",
        password="pgpassword_staging",
        sslmode="disable",
        connect_timeout=5
    )
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    print("Connected successfully!", flush=True)

    report = {}

    # List all tables in schema
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    all_tables = [r["table_name"] for r in cur.fetchall()]
    report["all_tables"] = all_tables
    print(f"Found {len(all_tables)} tables in schema.", flush=True)

    # Table Counts for key tables
    counts = {}
    for tbl in all_tables:
        try:
            cur.execute(f'SELECT count(*) FROM "{tbl}";')
            cnt = cur.fetchone()["count"]
            if cnt > 0:
                counts[tbl] = cnt
        except Exception as e:
            print(f"Error counting {tbl}: {e}", flush=True)
    report["table_counts_non_zero"] = counts
    print(f"Non-zero table counts: {counts}", flush=True)

    # 1. Part Categories
    if "part_partcategory" in all_tables:
        cur.execute("""
            SELECT id, name, pathstring, description, parent_id
            FROM part_partcategory
            ORDER BY id;
        """)
        report["categories"] = [dict(r) for r in cur.fetchall()]

    # 2. Parts (Products) sample (~25)
    if "part_part" in all_tables:
        cur.execute("""
            SELECT p.id, p.IPN, p.name, p.description, p.category_id, cat.pathstring as category_path,
                   p.assembly, p.component, p.purchaseable, p.salable, p.virtual, p.active, p.units, p.keywords
            FROM part_part p
            LEFT JOIN part_partcategory cat ON p.category_id = cat.id
            ORDER BY p.id
            LIMIT 30;
        """)
        parts = [dict(r) for r in cur.fetchall()]

        # Attach parameters and suppliers to parts
        for part in parts:
            pid = part["id"]
            if "part_partparameter" in all_tables and "part_partparametertemplate" in all_tables:
                cur.execute("""
                    SELECT t.name as param_name, param.data
                    FROM part_partparameter param
                    JOIN part_partparametertemplate t ON param.template_id = t.id
                    WHERE param.part_id = %s;
                """, (pid,))
                part["parameters"] = {r["param_name"]: r["data"] for r in cur.fetchall()}

            if "company_supplierpart" in all_tables and "company_company" in all_tables:
                cur.execute("""
                    SELECT sp.id, sp.SKU, c.name as supplier_name, sp.link, sp.note,
                           m.name as manufacturer_name, mp.MPN
                    FROM company_supplierpart sp
                    JOIN company_company c ON sp.supplier_id = c.id
                    LEFT JOIN company_manufacturerpart mp ON sp.manufacturer_part_id = mp.id
                    LEFT JOIN company_company m ON mp.manufacturer_id = m.id
                    WHERE sp.part_id = %s;
                """, (pid,))
                part["suppliers"] = [dict(r) for r in cur.fetchall()]

        report["parts_sample"] = parts

    # 3. Companies (Vendors/Manufacturers/Customers)
    if "company_company" in all_tables:
        cur.execute("""
            SELECT id, name, description, is_supplier, is_manufacturer, is_customer, website, phone, email
            FROM company_company
            ORDER BY id
            LIMIT 30;
        """)
        report["companies_sample"] = [dict(r) for r in cur.fetchall()]

    # 4. Supplier Parts
    if "company_supplierpart" in all_tables:
        cur.execute("""
            SELECT sp.id, sp.part_id, p.name as part_name, p.IPN as part_ipn,
                   c.name as supplier_name, sp.SKU, m.name as manufacturer_name, mp.MPN, sp.link
            FROM company_supplierpart sp
            JOIN part_part p ON sp.part_id = p.id
            JOIN company_company c ON sp.supplier_id = c.id
            LEFT JOIN company_manufacturerpart mp ON sp.manufacturer_part_id = mp.id
            LEFT JOIN company_company m ON mp.manufacturer_id = m.id
            ORDER BY sp.id
            LIMIT 30;
        """)
        report["supplier_parts_sample"] = [dict(r) for r in cur.fetchall()]

    # 5. Manufacturer Parts
    if "company_manufacturerpart" in all_tables:
        cur.execute("""
            SELECT mp.id, mp.part_id, p.name as part_name, c.name as manufacturer_name, mp.MPN, mp.description
            FROM company_manufacturerpart mp
            JOIN part_part p ON mp.part_id = p.id
            JOIN company_company c ON mp.manufacturer_id = c.id
            ORDER BY mp.id
            LIMIT 30;
        """)
        report["manufacturer_parts_sample"] = [dict(r) for r in cur.fetchall()]

    # 6. Stock Locations & Items
    if "stock_stocklocation" in all_tables:
        cur.execute("SELECT id, name, pathstring, description FROM stock_stocklocation ORDER BY id;")
        report["stock_locations"] = [dict(r) for r in cur.fetchall()]

    if "stock_stockitem" in all_tables:
        cur.execute("""
            SELECT si.id, si.part_id, p.name as part_name, si.quantity, sl.pathstring as location_path, si.status, si.batch, si.serial
            FROM stock_stockitem si
            LEFT JOIN part_part p ON si.part_id = p.id
            LEFT JOIN stock_stocklocation sl ON si.location_id = sl.id
            ORDER BY si.id
            LIMIT 30;
        """)
        report["stock_items_sample"] = [dict(r) for r in cur.fetchall()]

    out_file = "d:/WMS Ayusri/staging/inventree-staging-data/staging_data_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"SUCCESSFULLY exported staging data report to {out_file}", flush=True)

    cur.close()
    conn.close()

except Exception as e:
    print(f"Fatal error: {e}", flush=True)
    import traceback
    traceback.print_exc()
