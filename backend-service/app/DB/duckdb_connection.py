import duckdb
import os

#DB_PATH = os.getenv("DB_PATH", "./index.db")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "index.db"))

def get_connection():
    return duckdb.connect(database=DB_PATH, read_only=False)