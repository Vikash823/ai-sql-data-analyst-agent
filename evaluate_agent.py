import csv
import time
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from agent_graph_v2 import agent
from agent_tools import run_sql_query

TEST_CASES = [
    ('T01', 'How many total orders are there?',
     'SELECT COUNT(*) AS total_orders FROM orders'),
    ('T02', 'What is the total order amount for each city?',
     'SELECT city, SUM(order_amount) AS total_order_amount FROM orders GROUP BY city'),
    ('T03', 'Which store has the maximum number of rejected orders?',
     "SELECT store_id, COUNT(*) AS rejected_orders_count FROM orders WHERE order_status = 'REJECTED' GROUP BY store_id ORDER BY rejected_orders_count DESC, store_id LIMIT 1"),
    ('T04', 'Show the average order value for each store.',
     'SELECT store_id, AVG(order_amount) AS avg FROM orders GROUP BY store_id'),
    ('T05', 'What percentage of orders were rejected in each city?',
     "SELECT city, COUNT(*) FILTER (WHERE order_status='REJECTED') * 100.0 / NULLIF(COUNT(*), 0) AS rejection_rate FROM orders GROUP BY city"),
]


def normalized_value(value):
    try:
        return ('number', Decimal(str(value)).quantize(Decimal('0.01')))
    except (InvalidOperation, ValueError):
        return ('text', str(value).strip().casefold())


def compare_results(actual, expected):
    '''Compare result values, ignoring row order and harmless column alias differences.

    Note: this assumes both queries return columns in the same logical order.
    '''
    ac = actual.get('columns', [])
    ec = expected.get('columns', [])
    if len(ac) != len(ec):
        return False
    ar = actual.get('rows', [])
    er = expected.get('rows', [])
    if len(ar) != len(er):
        return False
    if any(len(row) != len(ac) for row in ar + er):
        return False
    a = Counter(tuple(normalized_value(v) for v in row) for row in ar)
    e = Counter(tuple(normalized_value(v) for v in row) for row in er)
    return a == e


def evaluate_case(case):
    test_id, question, reference_sql = case
    print(f'\nTesting {test_id}: {question}')
    started = time.perf_counter()
    try:
        expected = run_sql_query(reference_sql)
    except Exception as error:
        raise RuntimeError(f'Reference SQL failed for {test_id}: {error}') from error

    try:
        output = agent.invoke({
            'question': question, 'attempts': 0, 'error': '',
            'result': {}, 'insight': '', 'insight_success': False
        })
        actual = output.get('result', {})
        execution_success = bool(not output.get('error') and 'rows' in actual and 'columns' in actual)
        correct = bool(execution_success and compare_results(actual, expected))
        return {
            'test_id': test_id,
            'question': question,
            'execution_success': execution_success,
            'result_correct': correct,
            'insight_success': bool(output.get('insight_success', False)),
            'attempts': output.get('attempts', 0),
            'latency_seconds': round(time.perf_counter() - started, 2),
            'error': str(output.get('error', ''))[:200],
        }
    except Exception as error:
        return {
            'test_id': test_id, 'question': question,
            'execution_success': False, 'result_correct': False,
            'insight_success': False, 'attempts': 0,
            'latency_seconds': round(time.perf_counter() - started, 2),
            'error': type(error).__name__,
        }


def main():
    results = []
    for case in TEST_CASES:
        item = evaluate_case(case)
        results.append(item)
        print(('PASS' if item['result_correct'] else 'FAIL'), '|',
              item['latency_seconds'], 'seconds', '|', item['error'])

    total = len(results)
    correct = sum(row['result_correct'] for row in results)
    successful = sum(row['execution_success'] for row in results)
    insight_successes = sum(row['insight_success'] for row in results)
    avg_latency = sum(row['latency_seconds'] for row in results) / total

    print('\nEVALUATION SUMMARY')
    print(f'Total questions: {total}')
    print(f'Result correctness: {correct / total:.0%}')
    print(f'Execution success: {successful / total:.0%}')
    print(f'Insight generation success: {insight_successes / total:.0%}')
    print(f'Average end-to-end latency: {avg_latency:.2f} seconds')

    path = Path('evaluation_results/agent_evaluation.csv')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f'Report saved: {path}')


if __name__ == '__main__':
    main()
