import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

credentials_path = './855-keys.json'
credentials = service_account.Credentials.from_service_account_file(credentials_path)
project = "testproject-198108"

def run_bigquery_query(sql_query: str) -> pd.DataFrame:
    client = bigquery.Client(credentials=credentials, project=project)
    query_job = client.query(sql_query)

    results = query_job.result()
    total_bytes_processed = query_job.total_bytes_processed or 0
    print(f"Data Processed: {total_bytes_processed} bytes ({total_bytes_processed/1024/1024:.2f} MB)")

    df = results.to_dataframe()
    for col in df.select_dtypes(include=['float']).columns:
        df[col] = df[col].map(lambda x: f"{x:.6f}")
    return df
