
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key from .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Please check your .env file."
    )

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)


# Database schema provided to the LLM
DATABASE_SCHEMA = """
Database: PostgreSQL

Table: orders

Columns:
- order_id: INTEGER, primary key
- store_id: VARCHAR(20)
- city: VARCHAR(50)
- order_date: DATE
- order_amount: NUMERIC(10,2)
- order_status: VARCHAR(20)

Possible order_status values:
- DELIVERED
- REJECTED
"""


def generate_sql(question):
    """Convert a natural-language question into PostgreSQL SQL."""

    instructions = f"""
You are an expert PostgreSQL SQL generator.

Database schema:
{DATABASE_SCHEMA}

Rules:
1. Generate PostgreSQL-compatible SQL.
2. Use only tables and columns in the provided schema.
3. Generate exactly one read-only SELECT query.
4. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, TRUNCATE, or other modifying commands.
5. Use NULLIF to avoid division by zero.
6. Rejection rate = rejected orders / total orders * 100.
7. For questions without an explicit date range,
   do not apply an arbitrary date filter.
8. Return SQL only, without markdown or explanations.
9. If the question cannot be answered using the schema,
   return exactly: UNSUPPORTED_QUESTION.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=instructions,
            temperature=0
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    sql = response.text.strip()

    # Remove markdown fences if the model includes them
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.I)
    sql = re.sub(r"\s*```$", "", sql).strip()

    return sql
