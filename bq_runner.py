import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# Set credentials and initialize Vertex AI
credentials_path = './855-keys.json'
credentials = service_account.Credentials.from_service_account_file(credentials_path)
project="testproject-198108"

def run_bigquery_query(sql_query: str) -> list:
    client = bigquery.Client(credentials=credentials, project=project)
    query_job = client.query(sql_query)

    # Wait for job to complete
    results = query_job.result()

    # Now it's safe to access total_bytes_processed
    total_bytes_processed = query_job.total_bytes_processed or 0
    print(f"Data Processed: {total_bytes_processed} bytes ({total_bytes_processed/1024/1024:.2f} MB)")
    
    

    df = results.to_dataframe()
    print(df)
    for col in df.select_dtypes(include=['float']).columns:
        df[col] = df[col].map(lambda x: f"{x:.6f}")
    markdown_table = df.to_markdown(index=False)
    print(markdown_table)
    return markdown_table
    #return df.to_markdown(index=False)
    #return [dict(row) for row in results]
