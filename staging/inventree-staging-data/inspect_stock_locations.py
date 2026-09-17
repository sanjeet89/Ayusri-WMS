import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5433,
    dbname="inventree_staging",
    user="pguser_staging",
    password="pgpassword_staging"
)

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'stock_stocklocation';")
cols = cur.fetchall()
print("=== Columns in stock_stocklocation ===")
for c in cols:
    print(f"- {c['column_name']} ({c['data_type']})")

cur.execute("SELECT id, name, description, parent_id, structural, pathstring FROM stock_stocklocation LIMIT 10;")
rows = cur.fetchall()
print("\n=== Existing Stock Locations ===")
for r in rows:
    print(r)

conn.close()
