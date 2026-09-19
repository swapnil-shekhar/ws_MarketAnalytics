-- sector_performance.sql
-- Gold layer: Sector-level daily aggregates and returns

{{ config(materialized='table') }}

WITH stock_data AS (
    SELECT
        sp.ticker,
        sp.date,
        sp.close,
        sp.volume,
        td.sector
    FROM {{ source('clean', 'stock_prices') }} sp
    JOIN {{ source('clean', 'ticker_dim') }} td
        ON sp.ticker = td.ticker
),

sector_daily AS (
    SELECT
        sector,
        date,
        AVG(close) AS avg_close,
        AVG(volume) AS avg_volume
    FROM stock_data
    GROUP BY sector, date
),

sector_returns AS (
    SELECT
        sector,
        date,
        avg_close,
        avg_volume,
        (avg_close - LAG(avg_close, 1) OVER (PARTITION BY sector ORDER BY date))
            / LAG(avg_close, 1) OVER (PARTITION BY sector ORDER BY date) AS sector_return
    FROM sector_daily
)

SELECT
    sector,
    date,
    avg_close,
    avg_volume,
    sector_return,
    current_timestamp() AS processed_at
FROM sector_returns
WHERE sector_return IS NOT NULL