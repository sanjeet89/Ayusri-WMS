import psycopg2
import psycopg2.extras
import json
import sys

print("Starting DB connection...", flush=True)

hosts = [("inventree-staging-db", 5432), ("127.0.0.1", 5433), ("localhost", 5433)]
conn = None

for h, p in hosts:
    print(f"Trying host {h}:{p}...", flush=True)
    try:
        conn = psycopg2.connect(
            host=h,
            port=p,
            dbname="inventree_staging",
            user="pguser_staging",
            password="pgpassword_staging",
            connect_timeout=3
        )
        print(f"Connected successfully via {h}:{p}!", flush=True)
        break
    except Exception as e:
        print(f"Failed to connect via {h}:{p}: {e}", flush=True)

if not conn:
    print("Could not connect to database on any host!", flush=True)
    sys.exit(1)

try:
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    report = {}

    # Table Counts
    counts = {}
    tables = [
        "part_partcategory", "part_part", "company_company", 
        "company_supplierpart", "company_manufacturerpart",
        "stock_stocklocation", "stock_stockitem", "build_build",
        "order_purchaseorder", "order_salesorder", "part_partparameter"
    ]
    for tbl in tables:
        cur.execute(f"SELECT count(*) FROM {tbl};")
        counts[tbl] = cur.fetchone()["count"]
    print(f"Table counts: {counts}", flush=True)
    report["table_counts"] = counts

    # Categories
    cur.execute("""
        SELECT id, name, pathstring, description, parent_id
        FROM part_partcategory
        ORDER BY id;
    """)
    report["categories"] = [dict(r) for r in cur.fetchall()]

    # Parts (Sample ~20-25)
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
        # Parameters
        cur.execute("""
            SELECT t.name as param_name, param.data
            FROM part_partparameter param
            JOIN part_partparametertemplate t ON param.template_id = t.id
            WHERE param.part_id = %s;
        """, (pid,))
        part["parameters"] = {r["param_name"]: r["data"] for r in cur.fetchall()}

        # Supplier Parts
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

    # Companies (Sample ~20-25)
    cur.execute("""
        SELECT id, name, description, is_supplier, is_manufacturer, is_customer, website, phone, email
        FROM company_company
        ORDER BY id
        LIMIT 30;
    """)
    report["companies_sample"] = [dict(r) for r in cur.fetchall()]

    # Supplier Parts Sample
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

    # Manufacturer Parts Sample
    cur.execute("""
        SELECT mp.id, mp.part_id, p.name as part_name, c.name as manufacturer_name, mp.MPN, mp.description
        FROM company_manufacturerpart mp
        JOIN part_part p ON mp.part_id = p.id
        JOIN company_company c ON mp.manufacturer_id = c.id
        ORDER BY mp.id
        LIMIT 30;
    """)
    report["manufacturer_parts_sample"] = [dict(r) for r in cur.fetchall()]

    # Stock Locations & Items
    cur.execute("SELECT id, name, pathstring, description FROM stock_stocklocation ORDER BY id;")
    report["stock_locations"] = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT si.id, si.part_id, p.name as part_name, si.quantity, sl.pathstring as location_path, si.status, si.batch, si.serial
        FROM stock_stockitem si
        LEFT JOIN part_part p ON si.part_id = p.id
        LEFT JOIN stock_stocklocation sl ON si.location_id = sl.id
        ORDER BY si.id
        LIMIT 30;
    """)
    report["stock_items_sample"] = [dict(r) for r in cur.fetchall()]

    out_file = "/home/inventree/data/staging_data_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Report written successfully to {out_file}", flush=True)

    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
