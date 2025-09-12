from google.oauth2 import service_account
from google.cloud import aiplatform
import vertexai
from vertexai.preview.generative_models import GenerativeModel

# Set credentials and initialize Vertex AI
credentials_path = './855-keys.json'
credentials = service_account.Credentials.from_service_account_file(credentials_path)

vertexai.init(
    credentials=credentials,
    project="testproject-198108",
    location="us-central1"
)

# Load the Gemini model
gemini_model = GenerativeModel("gemini-1.5-flash")

# Load prompt context from external file
with open("prompt_context.txt", encoding="utf-8") as file:
    prompt_context = file.read()

def generate_sql_from_prompt(user_query: str) -> str:
    full_prompt = f"{prompt_context}\n\nNow generate SQL for this query: {user_query}"

    response = gemini_model.generate_content(
        full_prompt,
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 512,
            "top_p": 0.8,
            "top_k": 40,
        }
    )

    raw_sql = response.text.strip()
    print(raw_sql)

    try:
        usage_metadata = response._raw_response.usage_metadata
        prompt_tokens = usage_metadata.prompt_token_count
        completion_tokens = usage_metadata.candidates_token_count
        total_tokens = usage_metadata.total_token_count

        print(f"��� Prompt Tokens Used: {prompt_tokens}")
        print(f"��� Completion Tokens Used: {completion_tokens}")
        print(f"��� Total Tokens Used: {total_tokens}")
    except Exception as e:
        print(f"⚠️ Could not fetch token usage info: {e}")


    # ���️ Fix: Remove ```sql ... ``` wrappers if they exist
    if raw_sql.startswith("```"):
        raw_sql = raw_sql.strip('`')  # Remove all backticks
        if raw_sql.lower().startswith("sql"):
            raw_sql = raw_sql[3:].strip()  # Remove 'sql' word

    # ���️ Post-processing Validation
    #validate_generated_sql(raw_sql)
    #print(raw_sql)
    return raw_sql


def validate_generated_sql(sql: str):
    """ Basic validation to ensure Gemini generated a proper SQL """
    if not (sql.lower().startswith("select") or sql.lower().startswith("with")):
        raise ValueError("Generated SQL must start with SELECT")
    if "from" not in sql.lower():
        raise ValueError("Generated SQL must contain a FROM clause")
    if sql.count("(") != sql.count(")"):
        raise ValueError("Mismatched parentheses in generated SQL")
