from flask import Flask, request, jsonify, render_template, url_for
from gemini_sql_generator import generate_sql_from_prompt
from bq_runner import run_bigquery_query
from google.auth import exceptions
from google.cloud import aiplatform
from google.oauth2 import service_account
import os

os.environ['GOOGLE_CLOUD_PROJECT'] = 'testproject-198108'

# Initialize the AI platform with a service account key file
credentials_path = './855-keys.json'

try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    aiplatform.init(credentials=credentials, project="testproject-198108", location="us-central1")
except exceptions.DefaultCredentialsError:
    print("Error: Invalid credentials provided")

app = Flask(__name__)

# Route to display the initial query form
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
        print(f"Generated SQL for web query: {sql}")
        result = run_bigquery_query(sql)
        print("BigQuery query executed successfully for web query.")
        return render_template("query_page.html",
                               current_query=user_query,
                               submitted_query=user_query,
                               generated_sql=sql,
                               query_results=result)
    except Exception as e:
        print(f"Error processing web query '{user_query}': {e}")
        # traceback.print_exc() # Uncomment for detailed traceback during development
        return render_template("query_page.html", current_query=user_query, error_message=str(e))


@app.route("/billing-ai", methods=["GET", "POST"])
def billing_ai_handler():
    try:
        user_query = None
        if request.method == "POST":
            # For POST requests, get data from JSON body
            user_query = request.json.get("query")
        elif request.method == "GET":
            # For GET requests, get data from URL parameters
            user_query = request.args.get("query")

        if not user_query:
            return jsonify({"error": "Missing 'query' in request body"}), 400
        print("Working fine till here")
        sql = generate_sql_from_prompt(user_query)
        print("SQL Generator Working fine till here")
        print(sql)
        result = run_bigquery_query(sql)

        return jsonify({
            "query": user_query,
            "generated_sql": sql,
            "results": result
        })

    except Exception as e:
#        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

#   This starts the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
