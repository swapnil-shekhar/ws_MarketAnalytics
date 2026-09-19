# Databricks notebook source
# DBTITLE 1,Create Catalog Schemas and Volumes
# 00_create_catalog_schemas.py
# Creates UC catalogs, schemas, and volumes for the specified environment
# Uses DAB variable: catalog (e.g., fin_analytics_dev)

import json

catalog = dbutils.widgets.get("catalog") if "catalog" in [w.name for w in dbutils.widgets.getAll()] else "fin_analytics_dev"

schemas = ["raw", "clean", "gold"]
volumes = {
    "raw": ["raw_files", "reference_configs"],
    "clean": [],
    "gold": []
}

# Create catalog if it doesn't exist
try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
    print(f"Catalog '{catalog}' ready")
except Exception as e:
    print(f"Catalog '{catalog}' already exists or error: {e}")

# Create schemas
for schema in schemas:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
    print(f"Schema '{catalog}.{schema}' ready")

# Create volumes
for schema, vol_list in volumes.items():
    for vol in vol_list:
        try:
            spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.{vol}")
            print(f"Volume '{catalog}.{schema}.{vol}' ready")
        except Exception as e:
            print(f"Volume '{catalog}.{schema}.{vol}': {e}")

print(f"\nAll UC objects created for catalog: {catalog}")
spark.sql(f"SHOW SCHEMAS IN {catalog}").display()

# COMMAND ----------

