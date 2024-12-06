DROP TABLE IF EXISTS stocks;
CREATE TABLE stocks (
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    current_price REAL NOT NULL,
    description TEXT,
    sector TEXT,
    industry TEXT,
    market_cap TEXT,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (symbol)
);