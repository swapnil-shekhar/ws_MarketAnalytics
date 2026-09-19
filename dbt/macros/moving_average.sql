{% macro moving_average(column_name, period=20) %}
-- Simple Moving Average macro
-- Usage: {{ moving_average('close', 20) }}

AVG({{ column_name }}) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW)
{% endmacro %}