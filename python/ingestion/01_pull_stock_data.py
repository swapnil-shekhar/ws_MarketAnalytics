# Databricks notebook source
# DBTITLE 1,Pull Stock Data via yfinance
# Databricks notebook source
# 01_pull_stock_data.py
# BRONZE: Fetch OHLCV stock data via yfinance and write to raw Delta table
# Output: fin_analytics_<env>.raw.stock_prices_raw

import yfinance as yf
from pyspark.sql.types import *
import pandas as pd
from datetime import datetime, timedelta

catalog = dbutils.widgets.get("catalog") if "catalog" in [w.name for w in dbutils.widgets.getAll()] else "fin_analytics_dev"
table_name = f"{catalog}.raw.stock_prices_raw"

# Define tickers to fetch
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM",
    "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "BAC", "XOM",
    "PFE", "KO", "PEP", "CSCO", "NFLX", "ADBE", "CRM"
]

# Date range
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

all_data = []
for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        df.reset_index(inplace=True)
        df["ticker"] = ticker
        df["ingested_at"] = datetime.now()
        all_data.append(df)
        print(f"Fetched {ticker}: {len(df)} rows")
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

if all_data:
    pdf = pd.concat(all_data, ignore_index=True)
    pdf.columns = [c.lower().replace(" ", "_") for c in pdf.columns]
    
    spark_df = spark.createDataFrame(pdf)
    
    # Write to raw table (append mode for incremental ingestion)
    spark_df.write.mode("append").format("delta").saveAsTable(table_name)
    print(f"\nWrote {pdf.shape[0]} rows to {table_name}")
else:
    print("No data fetched")

spark.table(table_name).display()

# COMMAND ----------

