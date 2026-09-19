-- daily_returns.sql
-- Gold layer: Daily returns, rolling volatility, cumulative returns

{{ config(materialized='table') }}

WITH stock_data AS (
    SELECT ticker, date, close
    FROM {{ source('clean', 'stock_prices') }}
),

returns AS (
    SELECT
        ticker,
        date,
        close,
        (close - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date))
            / LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date) AS daily_return
    FROM stock_data
),

volatility AS (
    SELECT
        ticker,
        date,
        close,
        daily_return,
        -- 30-day rolling volatility (standard deviation of daily returns)
        STDDEV(daily_return) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS rolling_volatility_30d
    FROM returns
),

cumulative AS (
    SELECT
        ticker,
        date,
        close,
        daily_return,
        rolling_volatility_30d,
        -- Cumulative return (product of (1 + daily_return) - 1)
        EXP(SUM(LOG(1 + daily_return)) OVER (PARTITION BY ticker ORDER BY date)) - 1 AS cumulative_return
    FROM volatility
)

SELECT
    ticker,
    date,
    daily_return,
    rolling_volatility_30d,
    cumulative_return,
    current_timestamp() AS processed_at
FROM cumulative
WHERE daily_return IS NOT NULL