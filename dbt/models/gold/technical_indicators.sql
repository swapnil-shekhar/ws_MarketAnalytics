-- technical_indicators.sql
-- Gold layer: SMA, EMA, RSI, MACD, Bollinger Bands per ticker

{{ config(materialized='table') }}

WITH stock_data AS (
    SELECT ticker, date, close, volume
    FROM {{ source('clean', 'stock_prices') }}
),

windowed AS (
    SELECT
        ticker,
        date,
        close,
        volume,
        -- Simple Moving Averages
        AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS sma_20,
        AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS sma_50,
        -- Exponential Moving Averages
        AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS ema_12,
        AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) AS ema_26,
        -- Price changes for RSI
        close - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date) AS price_change
    FROM stock_data
),

rsi_calc AS (
    SELECT
        ticker,
        date,
        close,
        volume,
        sma_20,
        sma_50,
        ema_12,
        ema_26,
        price_change,
        CASE
            WHEN price_change > 0 THEN price_change
            ELSE 0
        END AS gain,
        CASE
            WHEN price_change < 0 THEN ABS(price_change)
            ELSE 0
        END AS loss
    FROM windowed
),

rsi_smooth AS (
    SELECT
        ticker,
        date,
        close,
        volume,
        sma_20,
        sma_50,
        ema_12,
        ema_26,
        AVG(gain) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_gain,
        AVG(loss) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_loss
    FROM rsi_calc
),

final AS (
    SELECT
        ticker,
        date,
        close,
        sma_20,
        sma_50,
        ema_12,
        ema_26,
        -- RSI
        CASE
            WHEN avg_loss = 0 THEN 100.0
            ELSE 100.0 - (100.0 / (1.0 + (avg_gain / avg_loss)))
        END AS rsi_14,
        -- MACD
        ema_12 - ema_26 AS macd,
        -- MACD Signal (9-period EMA of MACD)
        AVG(ema_12 - ema_26) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS macd_signal,
        -- Bollinger Bands (20-period SMA +/- 2 std dev)
        sma_20 + 2 * STDDEV(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS bollinger_upper,
        sma_20 - 2 * STDDEV(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS bollinger_lower,
        current_timestamp() AS processed_at
    FROM rsi_smooth
)

SELECT * FROM final