import pandas as pd
from google.cloud import bigquery

def run_bigquery_query(sql_query: str) -> list:
    client = bigquery.Client()
    query_job = client.query(sql_query)

    # Wait for job to complete
    results = query_job.result()

    # Now it's safe to access total_bytes_processed
    total_bytes_processed = query_job.total_bytes_processed or 0
    print(f"Data Processed: {total_bytes_processed} bytes ({total_bytes_processed/1024/1024:.2f} MB)")

    df = results.to_dataframe()
    print(df)
    return [dict(row) for row in results]
