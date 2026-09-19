# Databricks notebook source
# DBTITLE 1,Schema Definitions
# Databricks notebook source
# schema_definitions.py
# Centralized PySpark schema definitions for all tables

from pyspark.sql.types import *

# Raw layer schemas
stock_prices_raw_schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("date", DateType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("adj_close", DoubleType(), True),
    StructField("volume", LongType(), True),
    StructField("ingested_at", TimestampType(), True),
])

ticker_reference_raw_schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("company_name", StringType(), True),
    StructField("sector", StringType(), True),
    StructField("exchange", StringType(), True),
    StructField("ingested_at", TimestampType(), True),
])

# Clean layer schemas
stock_prices_schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("date", DateType(), False),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("adj_close", DoubleType(), True),
    StructField("volume", LongType(), True),
    StructField("ingested_at", TimestampType(), True),
    StructField("processed_at", TimestampType(), True),
])

ticker_dim_schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("company_name", StringType(), True),
    StructField("sector", StringType(), True),
    StructField("exchange", StringType(), True),
    StructField("ingested_at", TimestampType(), True),
    StructField("processed_at", TimestampType(), True),
])

# Gold layer schemas
technical_indicators_schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("date", DateType(), False),
    StructField("close", DoubleType(), True),
    StructField("sma_20", DoubleType(), True),
    StructField("sma_50", DoubleType(), True),
    StructField("ema_12", DoubleType(), True),
    StructField("ema_26", DoubleType(), True),
    StructField("rsi_14", DoubleType(), True),
    StructField("macd", DoubleType(), True),
    StructField("macd_signal", DoubleType(), True),
    StructField("bollinger_upper", DoubleType(), True),
    StructField("bollinger_lower", DoubleType(), True),
    StructField("processed_at", TimestampType(), True),
])

daily_returns_schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("date", DateType(), False),
    StructField("daily_return", DoubleType(), True),
    StructField("rolling_volatility_30d", DoubleType(), True),
    StructField("cumulative_return", DoubleType(), True),
    StructField("processed_at", TimestampType(), True),
])

sector_performance_schema = StructType([
    StructField("sector", StringType(), False),
    StructField("date", DateType(), False),
    StructField("avg_close", DoubleType(), True),
    StructField("avg_volume", LongType(), True),
    StructField("sector_return", DoubleType(), True),
    StructField("processed_at", TimestampType(), True),
])

# COMMAND ----------

