# Python Sales Pratice ETL Pipeline

## 1. Overview

This project is a simple ETL pipeline built with Python.  
It reads sales data from a CSV file, validates and cleans the data, then generates summary reports.

## 2. Project Goal

The goal of this project is to practice core Data Engineering concepts:

- Extract data from CSV
- Validate raw records
- Transform and clean data
- Aggregate sales metrics
- Export clean data and report files
- Use logging for pipeline monitoring

## 3. ETL Flow

```text
CSV File
→ Extract
→ Validate
→ Transform
→ Aggregate
→ Export CSV / JSON Report