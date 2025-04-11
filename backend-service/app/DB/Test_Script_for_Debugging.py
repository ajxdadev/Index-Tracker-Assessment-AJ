from duckdb_session import get_connection

conn = get_connection()

tables = conn.execute("SHOW TABLES").fetchall()
print("📦 Tables found:", tables)

for table_name in ("stock_metadata", "daily_price_data"):
    desc = conn.execute(f"DESCRIBE {table_name}").fetchall()
    print(f"\n {table_name} schema:")
    for col in desc:
        print(col)