'''
I can think of two approach here
1 - Ingest for all symbols in S&P 500
2 - Ingest for only top 100, basically sort on mkt cap before ingestion

Prefer to go ahead with #1, as it can help for any future scaling
Also, the data size is not multifold, hence safe to go ahead with #1
'''
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #added for local debug
#print("sys.path =", sys.path)
from bootstrap import *
from DB.duckdb_connection import get_connection
from core.get_symbols_list import get_sp500_symbols_from_ivv

def fetch_metadata(ticker_obj):
    info = ticker_obj.info
    return {
        "symbol": info.get("symbol"),
        "name": info.get("shortName"),
        "sector": info.get("sector"),
        "industry": info.get("industry")
    }


def fetch_price_data(ticker_obj, symbol):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=60)  # fetching 60 days, as it will give ~40 trading days data

    df = ticker_obj.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    df.reset_index(inplace=True)

    df = df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    # Append market cap and symbol to every row
    df["symbol"] = symbol
    df["market_cap"] = ticker_obj.info.get("marketCap", 0)

    return df[["symbol", "date", "open", "high", "low", "close", "volume", "market_cap"]]

def insert_metadata(conn, metadata_rows):
    df = pd.DataFrame(metadata_rows)
    if not df.empty:
        conn.execute("INSERT OR REPLACE INTO stock_metadata SELECT * FROM df")

def insert_price_data(conn, df):
    if not df.empty:
        conn.execute("INSERT OR REPLACE INTO daily_price_data SELECT * FROM df")

def main():
    conn = get_connection()
    #yfinance API rate limiter blocked requests hence added safeguarding
    SLEEP_BTWN_REQ = 1 
    RETRY_COUNT = 3
    metadata_rows = []
    price_dataframes = []

    #Fetch S&P500 symbols from public API
    all_symbols = get_sp500_symbols_from_ivv()

    #loop over symbols 
    for i, symbol in enumerate(all_symbols):
        print(f"[{i+1}/{len(all_symbols)}] Fetching: {symbol}")
        no_of_try = 0
        success = False
        while no_of_try < RETRY_COUNT and not success:
            try:
                ticker = yf.Ticker(symbol)

                #fetch metadata
                meta = fetch_metadata(ticker)
                metadata_rows.append(meta)

                #fetchprice and market cap
                df = fetch_price_data(ticker, symbol)
                price_dataframes.append(df)
                success = True
            except Exception as e:
                no_of_try += 1
                print(f" Attempt {no_of_try} out of {RETRY_COUNT} failed for {symbol}: {e}")
                time.sleep(3)
        
        time.sleep(SLEEP_BTWN_REQ)

    #store price and metadata in DuckDB
    insert_metadata(conn, metadata_rows)

    if price_dataframes:
        full_df = pd.concat(price_dataframes)
        insert_price_data(conn, full_df)

    conn.close()
    print("Ingestion complete")

if __name__ == "__main__":
    main()