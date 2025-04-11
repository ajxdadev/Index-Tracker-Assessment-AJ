-- Table: stock_metadata
CREATE TABLE IF NOT EXISTS stock_metadata (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    industry TEXT
);

-- Table: daily_price_data
CREATE TABLE IF NOT EXISTS daily_price_data (
    symbol TEXT,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    market_cap DOUBLE,
    PRIMARY KEY (symbol, date)
);