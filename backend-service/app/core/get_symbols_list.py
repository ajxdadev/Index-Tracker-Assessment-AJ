import pandas as pd
import requests
from io import StringIO

#Using publicly available CSV to get list of S&P 500 stocks
IVV_CSV_URL = (
    "https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/"
    "1467271812596.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund"
)

#Used AI to extract data out of this CSV in required format
def get_sp500_symbols_from_ivv():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(IVV_CSV_URL, headers=headers)
    response.raise_for_status()

    # Skip metadata/header section — data starts after row with "Ticker"
    csv_text = response.text
    start_idx = csv_text.find("Ticker")
    clean_csv = csv_text[start_idx:]

    df = pd.read_csv(StringIO(clean_csv))
    df = df.dropna(subset=["Ticker"])

    symbols = df["Ticker"].astype(str).str.strip().str.upper()
    symbols = [s.replace(".", "-") for s in symbols]  # BRK.B → BRK-B for yfinance
    #print(symbols)
    return symbols

Results = get_sp500_symbols_from_ivv()