from duckdb_connection import get_connection

def setup_duckDB():
    conn = get_connection()
    with open("app/DB/schema_definitions.sql", "r") as f:
        schema_sql = f.read()
    conn.execute(schema_sql)
    conn.close()
    print("DuckDB fired up!")

if __name__ == "__main__":
    setup_duckDB()