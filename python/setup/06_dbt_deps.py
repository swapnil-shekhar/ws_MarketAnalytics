# Databricks notebook source
# DBTITLE 1,dbt deps
# Databricks notebook source
# 06_dbt_deps.py
# Run dbt deps to install packages

import subprocess, os

dbt_project_dir = "/Workspace/Users/swapnilshekhar1493@gmail.com/ws_MarketAnalytics/dbt"
result = subprocess.run(["dbt", "deps", "--project-dir", dbt_project_dir], capture_output=True, text=True, cwd=dbt_project_dir)
print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    print("dbt deps completed successfully")

# COMMAND ----------

