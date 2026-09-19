-- Test: Assert no negative volumes in stock_prices

SELECT *
FROM {{ source('clean', 'stock_prices') }}
WHERE volume < 0