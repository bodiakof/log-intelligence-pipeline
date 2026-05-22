# Log Intelligence Pipeline

A local-first data engineering project that transforms raw simulated device logs into structured analytical data, SQL metrics, and dashboard insights.

This project was built as a trainee Data Engineering task. The goal is to demonstrate how raw semi-structured logs can be ingested, validated, transformed, analyzed, and visualized for monitoring and troubleshooting.

## Project Goals

The pipeline demonstrates:

- log data ingestion from simulated device sources
- validation of malformed, incomplete, and duplicate records
- separation between raw and processed data
- SQL-based transformations and analytical metrics
- storage in DuckDB, an embedded analytical database
- dashboard visualization for troubleshooting and monitoring
- basic data quality and pipeline observability

## Architecture

```text
Simulated device logs
        ↓
Raw JSONL files
        ↓
Python ingestion and validation
        ↓
DuckDB raw tables
        ↓
SQL transformations
        ↓
Processed analytical tables
        ↓
SQL metrics/views
        ↓
Streamlit dashboard
```

## Technology Choices

### Python

Python is used for log generation, ingestion, validation, orchestration, and pipeline control. It is widely used in data engineering and provides simple integration with local files, databases, and dashboard tools.

### DuckDB

DuckDB is used as the analytical storage engine. It is lightweight, local-first, SQL-friendly, and well-suited for analytical queries over structured data. It also allows the project to stay simple without requiring a separate database server.

### SQL

SQL is used for schema creation, transformations, aggregations, and metrics. This keeps analytical logic explicit and reviewable.

### Streamlit

Streamlit is used for the dashboard because it is easy to run locally and makes the visualization layer reproducible from the GitHub repository.

## Planned Pipeline Layers

| Layer | Responsibility |
|---|---|
| Ingestion | Read raw JSONL logs and load them into the raw table |
| Validation | Detect missing fields, invalid timestamps, invalid event types, malformed JSON, and duplicates |
| Processing | Normalize logs into structured analytical tables |
| Storage | Store raw and processed data in DuckDB |
| Analytics | Calculate metrics using SQL views |
| Visualization | Display monitoring and troubleshooting insights in Streamlit |
| Observability | Track processed records, rejected records, duplicates, and pipeline run status |

## Planned Metrics

The project will calculate metrics such as:

- total event volume over time
- error rate per device
- most frequent error codes
- device activity status
- warning/error trends
- mean time between errors
- simple error spike detection

## Local Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -e ".[dev]"
```

## Current Status

The project skeleton is initialized.

Next steps:

1. Add simulated device log generation.
2. Create DuckDB schema.
3. Implement ingestion, validation, and deduplication.
4. Add SQL transformations and metrics.
5. Build the Streamlit dashboard.