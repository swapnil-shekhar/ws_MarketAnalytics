# Databricks notebook source
# DBTITLE 1,Standardize Ticker Dimension
# 04_standardize_ticker_dim.py
# BRONZE to SILVER: Standardize ticker reference data
# Input: fin_analytics_<env>.raw.ticker_reference_raw
# Output: fin_analytics_<env>.clean.ticker_dim

from pyspark.sql.functions import *

catalog = dbutils.widgets.get("catalog") if "catalog" in [w.name for w in dbutils.widgets.getAll()] else "fin_analytics_dev"
source_table = f"{catalog}.raw.ticker_reference_raw"
target_table = f"{catalog}.clean.ticker_dim"

df = spark.table(source_table)

standardized = (df
    .dropDuplicates(["ticker"])
    .withColumn("ticker", upper(trim(col("ticker"))))
    .withColumn("company_name", trim(col("company_name")))
    .withColumn("sector", initcap(trim(col("sector"))))
    .withColumn("exchange", upper(trim(col("exchange"))))
    .filter(col("ticker").isNotNull())
    .withColumn("processed_at", current_timestamp())
    .select("ticker", "company_name", "sector", "exchange", "ingested_at", "processed_at")
)

standardized.write.mode("overwrite").format("delta").saveAsTable(target_table)
print(f"Standardized {standardized.count()} ticker records to {target_table}")

spark.table(target_table).display()

# COMMAND ----------

