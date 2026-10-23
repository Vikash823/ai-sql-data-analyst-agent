
from contextlib import closing

from db import get_connection
from sql_validator import validate_sql


def execute_query(sql):
    """Validate and execute SQL using read-only PostgreSQL."""

    safe_sql = validate_sql(sql)

    with closing(get_connection()) as conn:
        with conn:
            with conn.cursor() as cursor:

                # Enforce read-only access for this transaction.
                cursor.execute("SET TRANSACTION READ ONLY")

                # Stop queries that take longer than 5 seconds.
                cursor.execute(
                    "SET LOCAL statement_timeout = '5s'"
                )

                # Keep searches in the approved schema.
                cursor.execute(
                    "SET LOCAL search_path = public, pg_catalog"
                )

                cursor.execute(safe_sql)

                columns = [
                    description[0]
                    for description in cursor.description
                ]

                # Cap returned results at 100 rows.
                rows = cursor.fetchmany(101)

                if len(rows) > 100:
                    raise ValueError(
                        "Query returned more than 100 rows."
                    )

                return columns, rows
