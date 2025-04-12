import duckdb
import os

DB_PATH = os.getenv("DB_PATH", "app/index.db")

print(f"Using DuckDB at: {os.path.abspath(DB_PATH)}") #help local debug
print(f" File exists? {os.path.exists(DB_PATH)}") #help local debug
def get_connection():
    return duckdb.connect(database=DB_PATH, read_only=False)