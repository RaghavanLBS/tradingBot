CREATE TABLE fii_dii_data (
    trade_date TIMESTAMP,
    FII_Equity FLOAT,
    FII_Debt FLOAT,
    FII_Derivatives FLOAT,
    FII_Total FLOAT,
    MF_Total FLOAT,
    MF_Derivatives FLOAT,
    MF_Debt FLOAT,
    MF_Equity FLOAT
);
CREATE TABLE fii_equity (
    trade_date TIMESTAMP,
    equity_gross_purchase FLOAT,
    equity_gross_sales FLOAT,
    equity_net FLOAT,
    debt_gross_sales FLOAT,
    debt_gross_purchase FLOAT
);

CREATE TABLE fii_dii_data_monthly (
    "DATE" DATE,
    "FII Equity" FLOAT,
    "FII Debt" FLOAT,
    "FII Derivatives" FLOAT,
    "FII Total" FLOAT,
    "MF Total" FLOAT,
    "MF Derivatives" FLOAT,
    "MF Debt" FLOAT,
    "MF Equity" FLOAT
);

CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            date TEXT,
            trade_type TEXT,  -- 'BUY CE' or 'BUY PE'
            entry_reason TEXT,
            exit_reason TEXT,
            fii_value REAL,
            dii_value REAL,
            sentiment_score REAL,
            gpt_sentiment REAL,
            final_sentiment REAL
        )