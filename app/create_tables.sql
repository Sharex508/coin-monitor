-- Create the coin_monitor table
CREATE TABLE IF NOT EXISTS coin_monitor (
    id              SERIAL PRIMARY KEY,
    symbol          TEXT NOT NULL,
    initial_price   FLOAT NOT NULL,
    low_price       FLOAT NOT NULL,
    high_price      FLOAT NOT NULL,
    latest_price    FLOAT NOT NULL,
    low_price_1     FLOAT DEFAULT 0.0,
    high_price_1    FLOAT DEFAULT 0.0,
    low_price_2     FLOAT DEFAULT 0.0,
    high_price_2    FLOAT DEFAULT 0.0,
    low_price_3     FLOAT DEFAULT 0.0,
    high_price_3    FLOAT DEFAULT 0.0,
    low_price_4     FLOAT DEFAULT 0.0,
    high_price_4    FLOAT DEFAULT 0.0,
    low_price_5     FLOAT DEFAULT 0.0,
    high_price_5    FLOAT DEFAULT 0.0,
    low_price_6     FLOAT DEFAULT 0.0,
    high_price_6    FLOAT DEFAULT 0.0,
    low_price_7     FLOAT DEFAULT 0.0,
    high_price_7    FLOAT DEFAULT 0.0,
    low_price_8     FLOAT DEFAULT 0.0,
    high_price_8    FLOAT DEFAULT 0.0,
    low_price_9     FLOAT DEFAULT 0.0,
    high_price_9    FLOAT DEFAULT 0.0,
    low_price_10    FLOAT DEFAULT 0.0,
    high_price_10   FLOAT DEFAULT 0.0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a unique index on the symbol column
CREATE UNIQUE INDEX IF NOT EXISTS coin_monitor_symbol_idx ON coin_monitor (symbol);

-- No sample data - all coins will be initialized with current prices from Binance API
