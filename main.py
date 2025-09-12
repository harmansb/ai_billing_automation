from flask import Flask, request, jsonify, render_template
from gemini_sql_generator import generate_sql_from_prompt
from bq_runner import run_bigquery_query
from google.auth import exceptions
from google.cloud import aiplatform
from google.oauth2 import service_account
import os

os.environ['GOOGLE_CLOUD_PROJECT'] = 'testproject-198108'
credentials_path = './855-keys.json'

try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    aiplatform.init(credentials=credentials, project="testproject-198108", location="us-central1")
except exceptions.DefaultCredentialsError:
    print("Error: Invalid credentials provided")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("query_page.html")

@app.route("/ask", methods=["GET"])
def handle_query_submission():
    user_query = request.args.get("query")
    if not user_query:
        return render_template("query_page.html", error_message="Query parameter is missing.")

    try:
        print(f"Processing web query: {user_query}")
        sql = generate_sql_from_prompt(user_query)
        print(f"Generated SQL: {sql}")
        df = run_bigquery_query(sql)
        html_table = df.to_html(index=False, classes="table table-striped table-bordered", border=0, justify='center')
        return render_template("query_page.html",
                               current_query=user_query,
                               submitted_query=user_query,
                               generated_sql=sql,
                               query_results=html_table)
    except Exception as e:
        print(f"Error: {e}")
        return render_template("query_page.html", current_query=user_query, error_message=str(e))

@app.route("/billing-ai", methods=["GET", "POST"])
def billing_ai_handler():
    try:
        user_query = request.json.get("query") if request.method == "POST" else request.args.get("query")
        if not user_query:
            return jsonify({"error": "Missing 'query' in request body"}), 400

        sql = generate_sql_from_prompt(user_query)
        df = run_bigquery_query(sql)
        html_table = df.to_html(index=False, escape=False, classes="table table-striped table-bordered")
        return render_template("query_page.html",
                                current_query=user_query,
                                submitted_query=user_query,
                                generated_sql=sql,
                                query_results=html_table)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
