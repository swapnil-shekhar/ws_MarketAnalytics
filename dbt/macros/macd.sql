{% macro macd(column_name, fast=12, slow=26, signal=9) %}
-- MACD (Moving Average Convergence Divergence) macro
-- Usage: {{ macd('close', 12, 26, 9) }}

AVG({{ column_name }}) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ fast - 1 }} PRECEDING AND CURRENT ROW)
    - AVG({{ column_name }}) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ slow - 1 }} PRECEDING AND CURRENT ROW)
{% endmacro %}