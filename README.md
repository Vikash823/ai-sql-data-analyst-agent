
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

### 1. Clone the Repository

```bash
git clone https://github.com/Vikash823/ai-sql-data-analyst-agent.git
cd ai-sql-data-analyst-agent
```

### 2. Create a Python Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Create the PostgreSQL Database

Open pgAdmin and create a database named:

`ai_sql_agent`

Connect to this database as a PostgreSQL administrator.

Open Query Tool and execute:

`setup_database.sql`

This script creates the `orders` table and inserts 10 synthetic records.

**Note:** Run the setup script only on a fresh database to avoid duplicate sample orders.

### 4. Create a Read-Only Database User

Run the following commands in pgAdmin as an administrator:

```sql
CREATE ROLE ai_agent_reader
WITH LOGIN PASSWORD 'replace_with_strong_password';

GRANT CONNECT ON DATABASE ai_sql_agent
TO ai_agent_reader;

GRANT USAGE ON SCHEMA public
TO ai_agent_reader;

GRANT SELECT ON TABLE public.orders
TO ai_agent_reader;
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your PostgreSQL connection details, read-only user password, and Gemini API key.

Never commit `.env` to GitHub.

### 6. Start the FastAPI Backend

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

API documentation:

http://127.0.0.1:8000/docs

### 7. Start the Streamlit Dashboard

Open a second terminal:

```powershell
python -m streamlit run dashboard.py
```

Dashboard:

http://localhost:8501

### 8. Run Automated Evaluation

```powershell
python evaluate_agent.py
```

Evaluation results are saved to:

`evaluation_results/agent_evaluation.csv`


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
