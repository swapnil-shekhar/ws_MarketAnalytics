{% macro rsi(column_name, period=14) %}
-- RSI (Relative Strength Index) macro
-- Usage: {{ rsi('close', 14) }}

CASE
    WHEN AVG(CASE WHEN {{ column_name }} - LAG({{ column_name }}, 1) OVER (PARTITION BY ticker ORDER BY date) > 0
        THEN {{ column_name }} - LAG({{ column_name }}, 1) OVER (PARTITION BY ticker ORDER BY date)
        ELSE 0
    END) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW) = 0
    THEN 100.0
    ELSE 100.0 - (100.0 / (1.0 + (
        AVG(CASE WHEN {{ column_name }} - LAG({{ column_name }}, 1) OVER (PARTITION BY ticker ORDER BY date) > 0
            THEN {{ column_name }} - LAG({{ column_name }}, 1) OVER (PARTITION BY ticker ORDER BY date)
            ELSE 0
        END) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW)
        /
        AVG(CASE WHEN {{ column_name }} - LAG({{ column_name }}, 1) OVER (PARTITION BY ticker ORDER BY date) < 0
            THEN ABS({{ column_name }} - LAG({{ column_name }}, 1) OVER (PARTITION BY ticker ORDER BY date))
            ELSE 0
        END) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW)
    )))
END
{% endmacro %}