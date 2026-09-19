{% macro bollinger_bands(column_name, period=20, std_dev=2) %}
-- Bollinger Bands macro
-- Usage: {{ bollinger_bands('close', 20, 2) }}

AVG({{ column_name }}) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW)
    + {{ std_dev }} * STDDEV({{ column_name }}) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW)
AS bollinger_upper,
AVG({{ column_name }}) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW)
    - {{ std_dev }} * STDDEV({{ column_name }}) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN {{ period - 1 }} PRECEDING AND CURRENT ROW)
AS bollinger_lower
{% endmacro %}