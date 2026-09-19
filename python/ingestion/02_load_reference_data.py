# Databricks notebook source
# DBTITLE 1,Load Reference Data
# 02_load_reference_data.py
# BRONZE: Load ticker reference data (symbols, sectors, exchanges)
# Output: fin_analytics_<env>.raw.ticker_reference_raw

from pyspark.sql.types import *
import pandas as pd

catalog = dbutils.widgets.get("catalog") if "catalog" in [w.name for w in dbutils.widgets.getAll()] else "fin_analytics_dev"
table_name = f"{catalog}.raw.ticker_reference_raw"

# Reference data: ticker, company_name, sector, exchange
reference_data = [
    ("AAPL", "Apple Inc.", "Technology", "NASDAQ"),
    ("MSFT", "Microsoft Corporation", "Technology", "NASDAQ"),
    ("GOOGL", "Alphabet Inc.", "Communication Services", "NASDAQ"),
    ("AMZN", "Amazon.com Inc.", "Consumer Discretionary", "NASDAQ"),
    ("META", "Meta Platforms Inc.", "Communication Services", "NASDAQ"),
    ("NVDA", "NVIDIA Corporation", "Technology", "NASDAQ"),
    ("TSLA", "Tesla Inc.", "Consumer Discretionary", "NASDAQ"),
    ("JPM", "JPMorgan Chase & Co.", "Financials", "NYSE"),
    ("V", "Visa Inc.", "Financials", "NYSE"),
    ("JNJ", "Johnson & Johnson", "Healthcare", "NYSE"),
    ("WMT", "Walmart Inc.", "Consumer Staples", "NYSE"),
    ("PG", "Procter & Gamble", "Consumer Staples", "NYSE"),
    ("MA", "Mastercard Inc.", "Financials", "NYSE"),
    ("UNH", "UnitedHealth Group", "Healthcare", "NYSE"),
    ("HD", "The Home Depot", "Consumer Discretionary", "NYSE"),
    ("DIS", "The Walt Disney Company", "Communication Services", "NYSE"),
    ("BAC", "Bank of America", "Financials", "NYSE"),
    ("XOM", "Exxon Mobil", "Energy", "NYSE"),
    ("PFE", "Pfizer Inc.", "Healthcare", "NYSE"),
    ("KO", "The Coca-Cola Company", "Consumer Staples", "NYSE"),
    ("PEP", "PepsiCo Inc.", "Consumer Staples", "NASDAQ"),
    ("CSCO", "Cisco Systems", "Technology", "NASDAQ"),
    ("NFLX", "Netflix Inc.", "Communication Services", "NASDAQ"),
    ("ADBE", "Adobe Inc.", "Technology", "NASDAQ"),
    ("CRM", "Salesforce Inc.", "Technology", "NYSE"),
]

schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("company_name", StringType(), True),
    StructField("sector", StringType(), True),
    StructField("exchange", StringType(), True),
])

spark_df = spark.createDataFrame(reference_data, schema)
spark_df = spark_df.withColumn("ingested_at", current_timestamp())

spark_df.write.mode("overwrite").format("delta").saveAsTable(table_name)
print(f"Loaded {len(reference_data)} ticker records to {table_name}")

spark.table(table_name).display()

# COMMAND ----------

