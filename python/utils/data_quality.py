# Databricks notebook source
# DBTITLE 1,Data Quality Functions
# Databricks notebook source
# data_quality.py
# Reusable data quality validation functions

from pyspark.sql.functions import *
from pyspark.sql import DataFrame

def check_nulls(df, table_name="table"):
    """Check for null values in all columns and report."""
    null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
    nulls = null_counts.collect()[0].asDict()
    issues = {k: v for k, v in nulls.items() if v > 0}
    if issues:
        print(f"[{table_name}] NULL values found: {issues}")
    else:
        print(f"[{table_name}] No null values found")
    return issues

def check_duplicates(df, key_columns, table_name="table"):
    """Check for duplicate rows based on key columns."""
    total = df.count()
    unique = df.dropDuplicates(key_columns).count()
    duplicates = total - unique
    if duplicates > 0:
        print(f"[{table_name}] {duplicates} duplicate rows found on {key_columns}")
    else:
        print(f"[{table_name}] No duplicates found on {key_columns}")
    return duplicates

def validate_ranges(df, column, min_val=None, max_val=None, table_name="table"):
    """Validate that column values fall within expected range."""
    violations = 0
    if min_val is not None:
        violations += df.filter(col(column) < min_val).count()
    if max_val is not None:
        violations += df.filter(col(column) > max_val).count()
    if violations > 0:
        print(f"[{table_name}] {violations} rows in column '{column}' out of range [{min_val}, {max_val}]")
    else:
        print(f"[{table_name}] Column '{column}' within valid range")
    return violations

def run_all_checks(df, key_columns, table_name="table", range_checks=None):
    """Run all data quality checks."""
    print(f"\n=== Data Quality Report: {table_name} ===")
    nulls = check_nulls(df, table_name)
    dups = check_duplicates(df, key_columns, table_name)
    range_issues = 0
    if range_checks:
        for col_name, min_v, max_v in range_checks:
            range_issues += validate_ranges(df, col_name, min_v, max_v, table_name)
    print(f"\nSummary: {len(nulls)} null issues, {dups} duplicates, {range_issues} range violations")
    return len(nulls) == 0 and dups == 0 and range_issues == 0

# COMMAND ----------

