# Databricks notebook source
# DBTITLE 1,Test Ingestion
# test_ingestion.py
# Project-level test: verify ingestion produced data

from pyspark.sql.functions import *

catalog = "fin_analytics_dev"

# Test 1: stock_prices_raw has data
raw_count = spark.table(f"{catalog}.raw.stock_prices_raw").count()
assert raw_count > 0, f"FAIL: {catalog}.raw.stock_prices_raw is empty"
print(f"PASS: stock_prices_raw has {raw_count} rows")

# Test 2: ticker_reference_raw has data
ref_count = spark.table(f"{catalog}.raw.ticker_reference_raw").count()
assert ref_count > 0, f"FAIL: {catalog}.raw.ticker_reference_raw is empty"
print(f"PASS: ticker_reference_raw has {ref_count} rows")

# Test 3: No duplicate tickers in reference
dupes = spark.table(f"{catalog}.raw.ticker_reference_raw").groupBy("ticker").count().filter("count > 1").count()
assert dupes == 0, f"FAIL: {dupes} duplicate tickers found"
print(f"PASS: No duplicate tickers")

# Test 4: All expected tickers present
expected = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
actual = [row.ticker for row in spark.table(f"{catalog}.raw.stock_prices_raw").select("ticker").distinct().collect()]
for t in expected:
    assert t in actual, f"FAIL: {t} not found in stock_prices_raw"
print(f"PASS: All expected tickers present")

print("\n=== All ingestion tests passed ===")

# COMMAND ----------

