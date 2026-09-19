# Databricks notebook source
# DBTITLE 1,Install dbt
# Databricks notebook source
# 05_install_dbt.py
# Install dbt-databricks adapter

import subprocess
result = subprocess.run(["pip", "install", "dbt-databricks==1.8.0"], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    print("dbt-databricks installed successfully")

# COMMAND ----------

