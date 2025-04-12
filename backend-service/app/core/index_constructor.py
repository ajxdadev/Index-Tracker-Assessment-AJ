import pandas as pd
import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #added for local debug
from DB.duckdb_connection import get_connection

TOP_N = 100
BASE_INDEX_VALUE = 1000
DAYS_TO_TRACK = 30

def build_index():
    conn = get_connection()

    # Ensure the table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_index_history (
            date DATE PRIMARY KEY,
            index_value DOUBLE
        )
    """)

    # Get available trading days
    days = conn.execute("SELECT DISTINCT date FROM daily_price_data ORDER BY date").fetchall()
    dates = [d[0] for d in days]

    if len(dates) < DAYS_TO_TRACK + 1:
        raise Exception(f"Not enough trading days to compute index.")

    # We need T-1 to Tn (31 days)
    relevant = dates[-(DAYS_TO_TRACK + 1):]

    index_value = BASE_INDEX_VALUE
    final_values = []

    for i in range(1, len(relevant)):
        today = relevant[i]
        yesterday = relevant[i - 1]

        # Get top 100 by market cap for "today"
        top100 = conn.execute(f"""
            SELECT symbol
            FROM daily_price_data
            WHERE date = '{today}' AND market_cap IS NOT NULL
            ORDER BY market_cap DESC
            LIMIT {TOP_N}
        """).fetchall()
        symbols = [s[0] for s in top100]

        if len(symbols) < TOP_N:
            print(f"Skipping {today}: only {len(symbols)} stocks found")
            continue

        # Get closing prices for today and yesterday
        symbol_str = "', '".join(symbols)
        query = f"""
            SELECT symbol, date, close
            FROM daily_price_data
            WHERE symbol IN ('{symbol_str}') AND date IN ('{yesterday}', '{today}')
        """
        df = pd.DataFrame(conn.execute(query).fetchall(), columns=["symbol", "date", "close"])
        if df.empty:
            print(f" No data for {today}")
            continue

        #filter any values which doesn't exist 
        pivoted = df.pivot(index="symbol", columns="date", values="close").dropna()

        if pivoted.empty:
            print(f" Not enough data for {today}")
            continue

        pivoted["return"] = (pivoted[today] - pivoted[yesterday]) / pivoted[yesterday]
        avg_return = pivoted["return"].mean()

        index_value = index_value * (1 + avg_return)
        final_values.append((today, index_value))

        print(f"{today}: Index = {index_value:.2f} | Avg return = {avg_return:.4%}")

    # Write to DB
    if final_values:
        conn.execute("DELETE FROM custom_index_history")
        conn.executemany("INSERT INTO custom_index_history VALUES (?, ?)", final_values)

    conn.close()
    print("Index computation complete.")

if __name__ == "__main__":
    build_index()