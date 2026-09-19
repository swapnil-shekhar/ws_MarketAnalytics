# Databricks notebook source
# DBTITLE 1,Standardize Stock Prices
# Databricks notebook source
# 03_standardize_stock_prices.py
# BRONZE to SILVER: Standardize raw stock prices
# Input: fin_analytics_<env>.raw.stock_prices_raw
# Output: fin_analytics_<env>.clean.stock_prices

from pyspark.sql.functions import *
from pyspark.sql.types import *

catalog = dbutils.widgets.get("catalog") if "catalog" in [w.name for w in dbutils.widgets.getAll()] else "fin_analytics_dev"
source_table = f"{catalog}.raw.stock_prices_raw"
target_table = f"{catalog}.clean.stock_prices"

# Read raw data
df = spark.table(source_table)

# Standardize: type-cast, deduplicate, handle nulls
standardized = (df
    .dropDuplicates(["ticker", "date"])
    .withColumn("date", to_date(col("date")))
    .withColumn("open", col("open").cast("double"))
    .withColumn("high", col("high").cast("double"))
    .withColumn("low", col("low").cast("double"))
    .withColumn("close", col("close").cast("double"))
    .withColumn("volume", col("volume").cast("long"))
    .withColumn("adj_close", col("adj_close").cast("double"))
    .filter(col("close").isNotNull() & col("volume").isNotNull())
    .withColumn("processed_at", current_timestamp())
    .select("ticker", "date", "open", "high", "low", "close", "volume", "adj_close", "ingested_at", "processed_at")
)

standardized.write.mode("overwrite").format("delta").saveAsTable(target_table)
print(f"Standardized {standardized.count()} rows to {target_table}")

# Optimize
spark.sql(f"OPTIMIZE {target_table} ZORDER BY (ticker, date)")
print("Table optimized")

spark.table(target_table).display()

# COMMAND ----------

