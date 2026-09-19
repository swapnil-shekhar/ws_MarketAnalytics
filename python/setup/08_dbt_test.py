# Databricks notebook source
# DBTITLE 1,dbt test
# 08_dbt_test.py
# Run dbt tests on gold models

catalog = dbutils.widgets.get("catalog") if "catalog" in [w.name for w in dbutils.widgets.getAll()] else "fin_analytics_dev"
target = "dev" if "dev" in catalog else "qa" if "qa" in catalog else "prod"

import subprocess

dbt_project_dir = "/Workspace/Users/swapnilshekhar1493@gmail.com/ws_MarketAnalytics/dbt"
result = subprocess.run(
    ["dbt", "test", "--project-dir", dbt_project_dir, "--target", target],
    capture_output=True, text=True, cwd=dbt_project_dir
)
print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    print(f"dbt test completed successfully (target: {target})")

# COMMAND ----------

