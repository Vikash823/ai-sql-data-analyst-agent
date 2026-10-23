import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from langgraph.graph import END, START, StateGraph

from agent_tools import run_sql_query
from insight_service import generate_insights
from llm_service import DATABASE_SCHEMA

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError('GEMINI_API_KEY is missing from .env')

client = genai.Client(api_key=API_KEY)
MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
MAX_ATTEMPTS = 2

sql_tool = types.FunctionDeclaration(
    name='run_sql_query',
    description='Execute a validated read-only PostgreSQL SELECT against the approved orders table.',
    parameters_json_schema={
        'type': 'object',
        'properties': {'sql': {'type': 'string', 'description': 'One PostgreSQL SELECT query'}},
        'required': ['sql'],
    },
)


class AgentState(TypedDict, total=False):
    question: str
    sql: str
    attempts: int
    error: str
    result: dict
    insight: str
    insight_success: bool
    answer: str


def agent_node(state: AgentState):
    attempt = state.get('attempts', 0) + 1
    print(f'\n[AGENT] Attempt {attempt}')

    prompt = f'''You are an AI SQL Data Analyst.
DATABASE SCHEMA:
{DATABASE_SCHEMA}

USER QUESTION:
{state['question']}

Rules:
- Use only the orders table and its documented columns.
- Produce exactly one PostgreSQL SELECT query via run_sql_query.
- Never modify data or query other tables.
- Rejection rate = rejected order count * 100 / total order count.
- Use NULLIF to avoid division by zero.
- Do not add arbitrary date filters.
- Include relevant total counts when explaining rates, if the question permits.
- Do not invent missing columns or data.

Previous SQL validation error (if any): {state.get('error') or 'None'}
Correct the SQL if the previous query failed validation.
'''

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=[sql_tool])],
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode='ANY', allowed_function_names=['run_sql_query']
                    )
                ),
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                temperature=0,
            ),
        )
        calls = response.function_calls or []
        if len(calls) != 1 or calls[0].name != 'run_sql_query':
            raise ValueError('Expected exactly one run_sql_query tool call')
        sql = dict(calls[0].args or {}).get('sql')
        if not isinstance(sql, str) or not sql.strip():
            raise ValueError('Gemini did not supply SQL')

        print('[TOOL REQUEST] run_sql_query')
        print(sql)
        return {'sql': sql, 'attempts': attempt, 'error': '', 'result': {},
                'insight': '', 'insight_success': False}

    except errors.APIError as error:
        code = getattr(error, 'code', 'unknown')
        status = getattr(error, 'status', 'unknown')
        print(f'[GEMINI API ERROR] HTTP {code} | {status}')
        return {'sql': '', 'attempts': attempt,
                'error': f'Gemini API request failed (HTTP {code}).'}
    except Exception as error:
        print(f'[AGENT ERROR] {type(error).__name__}')
        return {'sql': '', 'attempts': attempt,
                'error': 'SQL generation or tool calling failed.'}


def route_agent(state: AgentState):
    return 'finish' if state.get('error') or not state.get('sql') else 'execute'


def execute_node(state: AgentState):
    print('\n[TOOL] Validating and executing SQL...')
    try:
        result = run_sql_query(state['sql'])
        print('[TOOL] Execution successful')
        return {'result': result, 'error': ''}
    except ValueError as error:
        # Only validation failures are candidates for SQL correction.
        print(f'[VALIDATION FAILED] {error}')
        return {'result': {}, 'error': f'SQL validation failed: {str(error)[:250]}'}
    except Exception as error:
        # Do not expose DB details to the model or end user.
        print(f'[DATABASE ERROR] {type(error).__name__}')
        return {'result': {}, 'error': 'Database execution failed; SQL retry disabled.'}


def route_after_execution(state: AgentState):
    error = state.get('error', '')
    if error:
        if error.startswith('SQL validation failed:') and state.get('attempts', 0) < MAX_ATTEMPTS:
            return 'retry'
        return 'finish'
    return 'insights'


def insight_node(state: AgentState):
    print('\n[INSIGHT] Generating business analysis...')
    result = state.get('result', {})
    if result.get('row_count', 0) == 0:
        return {'insight': 'No matching records found.', 'insight_success': True}
    try:
        insight = generate_insights(state['question'], result)
        print('[INSIGHT] Analysis generated')
        return {'insight': insight, 'insight_success': True}
    except errors.APIError as error:
        print(f'[INSIGHT API ERROR] HTTP {getattr(error, "code", "unknown")}')
    except Exception as error:
        print(f'[INSIGHT ERROR] {type(error).__name__}')
    return {'insight': 'AI analysis unavailable; see raw database results.',
            'insight_success': False}


def finish_node(state: AgentState):
    if state.get('error'):
        return {'answer': 'Query could not be completed.\n' + state['error']}
    result = state.get('result', {})
    if not result:
        return {'answer': 'No query result available.'}
    return {'answer': (
        'AI BUSINESS ANALYSIS\n--------------------------\n'
        + state.get('insight', 'No insight generated.')
        + '\n\nRAW DATABASE RESULTS\n--------------------------\n'
        + json.dumps(result, indent=2, default=str)
    )}


workflow = StateGraph(AgentState)
workflow.add_node('agent', agent_node)
workflow.add_node('execute', execute_node)
workflow.add_node('insights', insight_node)
workflow.add_node('finish', finish_node)
workflow.add_edge(START, 'agent')
workflow.add_conditional_edges('agent', route_agent, {
    'execute': 'execute', 'finish': 'finish'
})
workflow.add_conditional_edges('execute', route_after_execution, {
    'retry': 'agent', 'insights': 'insights', 'finish': 'finish'
})
workflow.add_edge('insights', 'finish')
workflow.add_edge('finish', END)
agent = workflow.compile()
