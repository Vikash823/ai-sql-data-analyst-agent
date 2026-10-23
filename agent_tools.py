
from query_executor import execute_query


def run_sql_query(sql: str):
    """
    Execute a validated, read-only SQL query.

    Args:
        sql: A PostgreSQL SELECT query.
    """

    columns, rows = execute_query(sql)

    return {
        "columns": columns,
        "rows": [
            [str(value) for value in row]
            for row in rows
        ],
        "row_count": len(rows)
    }
