
from google.genai import errors
from insight_service import generate_insights

question = "Which 3 stores have the highest rejection rate?"

result = {
    "columns": ["store_id", "rejection_rate"],
    "rows": [
        ["S104", "100.00"],
        ["S102", "66.67"],
        ["S101", "33.33"]
    ],
    "row_count": 3
}

try:
    insight = generate_insights(question, result)
    print("\nAI BUSINESS INSIGHT:")
    print(insight)

except errors.APIError as error:
    print("Gemini API error")
    print("Status code:", error.code)
    print("Error type:", type(error).__name__)

except Exception as error:
    print("Error type:", type(error).__name__)
    print("Details:", str(error)[:400])
