-- =====================================================================
-- Price analytics in SQL (ANSI window functions; runs on PostgreSQL,
-- Snowflake, BigQuery, and SQL Server with minor dialect tweaks).
-- Assumes a prices table: trade_date, ticker, open, high, low, close,
-- volume — the same shape as data/prices.csv.
-- =====================================================================

-- Q1. Daily returns per ticker
SELECT
    trade_date,
    ticker,
    close,
    close / LAG(close) OVER (PARTITION BY ticker ORDER BY trade_date) - 1
        AS daily_return
FROM prices
ORDER BY ticker, trade_date;

-- Q2. 50-day and 200-day simple moving averages, with the trend flag
--     analysts actually watch (price above/below the 200-day)
SELECT
    trade_date,
    ticker,
    close,
    AVG(close) OVER (PARTITION BY ticker ORDER BY trade_date
                     ROWS BETWEEN 49 PRECEDING AND CURRENT ROW)  AS sma_50,
    AVG(close) OVER (PARTITION BY ticker ORDER BY trade_date
                     ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma_200,
    CASE WHEN close > AVG(close) OVER (PARTITION BY ticker ORDER BY trade_date
                     ROWS BETWEEN 199 PRECEDING AND CURRENT ROW)
         THEN 'ABOVE' ELSE 'BELOW' END AS vs_sma200
FROM prices
ORDER BY ticker, trade_date;

-- Q3. Rolling 30-day realized volatility (annualized)
SELECT
    trade_date,
    ticker,
    STDDEV(daily_return) OVER (PARTITION BY ticker ORDER BY trade_date
                     ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
        * SQRT(252) AS rolling_vol_30d
FROM (
    SELECT trade_date, ticker,
           close / LAG(close) OVER (PARTITION BY ticker ORDER BY trade_date) - 1
               AS daily_return
    FROM prices
) r
WHERE daily_return IS NOT NULL
ORDER BY ticker, trade_date;

-- Q4. Running peak and drawdown from peak, per ticker
SELECT
    trade_date,
    ticker,
    close,
    MAX(close) OVER (PARTITION BY ticker ORDER BY trade_date) AS running_peak,
    close / MAX(close) OVER (PARTITION BY ticker ORDER BY trade_date) - 1
        AS drawdown_from_peak
FROM prices
ORDER BY ticker, trade_date;

-- Q5. Monthly OHLC rollup from daily bars
SELECT
    ticker,
    DATE_TRUNC('month', trade_date) AS month,
    ARG_MIN(open, trade_date)  AS month_open,
    MAX(high)                  AS month_high,
    MIN(low)                   AS month_low,
    ARG_MAX(close, trade_date) AS month_close,
    SUM(volume)                AS month_volume
FROM prices
GROUP BY ticker, DATE_TRUNC('month', trade_date)
ORDER BY ticker, month;
