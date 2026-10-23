
# AI SQL Data Analyst Agent

An Agentic AI application that converts natural-language
business questions into PostgreSQL queries, executes
validated read-only SQL, and generates business insights.

## Features

- Natural language to SQL using Google Gemini
- LLM function calling
- Stateful workflow using LangGraph
- SQL validation using SQLGlot
- Read-only PostgreSQL execution
- Limited SQL correction retries
- AI-generated business insights
- FastAPI backend
- Streamlit dashboard with automatic charts
- Automated SQL evaluation

## Architecture

User Question
    ↓
Streamlit Dashboard
    ↓
FastAPI
    ↓
LangGraph + Gemini
    ↓
SQL Tool Calling
    ↓
SQLGlot Validation
    ↓
PostgreSQL (Read Only)
    ↓
Business Insights + Results + Charts

## Technology Stack

Python | Gemini API | LangGraph | PostgreSQL
SQLGlot | FastAPI | Streamlit | Pandas

## Evaluation

Five analytical questions were evaluated against
reference SQL results on a small synthetic dataset.

- Result correctness: 5/5 (100%)
- SQL execution success: 5/5 (100%)
- Average latency: 2.55 seconds
- Insight generation disabled during this evaluation

These are preliminary SQL-only results, not
production accuracy benchmarks.

## Local Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies using requirements.txt.
4. Create .env from .env.example.
5. Configure PostgreSQL and create the sample orders table.
6. Use a restricted read-only database role.

Start the backend:

    python -m uvicorn api:app --host 127.0.0.1 --port 8000

Start the dashboard:

    python -m streamlit run dashboard.py

## Example Questions

- Which stores have the highest rejection rates?
- What is the total order amount by city?
- Which store has the most rejected orders?
- What is the average order value per store?

## Security

The application uses SQL validation and a restricted
read-only database account. This is a demonstration
project and is not approved for public production use.

## Limitations

- Demonstration uses synthetic data
- SQL grammar is intentionally restricted
- API quota limits may affect availability
- AI-generated insights require verification
- Authentication and broader security tests are pending
