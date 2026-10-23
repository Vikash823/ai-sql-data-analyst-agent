
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


ALLOWED_TABLES = {"orders"}

ALLOWED_COLUMNS = {
    "order_id",
    "store_id",
    "city",
    "order_date",
    "order_amount",
    "order_status",
}

# Allowed SQL syntax tree nodes.
# Anything not listed here is rejected by default.
ALLOWED_NODES = {
    # Basic SELECT structure
    "Select",
    "From",
    "Where",
    "Filter",
    "Table",
    "Column",
    "Identifier",
    "Alias",
    "Star",
    "Literal",
    "Null",
    "Paren",

    # Grouping and sorting
    "Group",
    "Order",
    "Ordered",
    "Limit",
    "Distinct",

    # Aggregation and supported functions
    "Count",
    "Sum",
    "Avg",
    "Min",
    "Max",
    "Round",
    "Nullif",
    "Coalesce",

    # CASE WHEN structure
    "Case",
    "If",

    # Mathematical operations
    "Add",
    "Sub",
    "Mul",
    "Div",
    "Mod",
    "Neg",

    # Conditions
    "EQ",
    "NEQ",
    "GT",
    "GTE",
    "LT",
    "LTE",
    "And",
    "Or",
    "Not",
    "Is",
    "Between",
    "In",

    # Common type conversions
    "Cast",
    "DataType",
    "DataTypeParam",

    # Date-based analysis
    "CurrentDate",
    "DateAdd",
    "DateSub",
    "Extract",
    "DateTrunc",
    "Year",
    "Month",
    "Day",
}


def validate_sql(sql):
    """
    Validate a restricted PostgreSQL SELECT query.

    Returns validated SQL text.
    Raises ValueError for unsupported queries.
    """

    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    if sql.strip() == "UNSUPPORTED_QUESTION":
        raise ValueError(
            "Question is not supported by the database."
        )

    # 1. Parse SQL
    try:
        statements = sqlglot.parse(
            sql,
            read="postgres",
            error_level="RAISE"
        )
    except (ParseError, ValueError) as error:
        raise ValueError(
            f"Invalid SQL syntax: {error}"
        ) from error

    # 2. Allow exactly one statement
    if len(statements) != 1 or statements[0] is None:
        raise ValueError(
            "Only one SQL statement is allowed."
        )

    tree = statements[0]

    # 3. Only plain SELECT
    if not isinstance(tree, exp.Select):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    # 4. Check entire syntax tree.
    # This also blocks unknown or unsafe function calls.
    for node in tree.walk():

        node_name = type(node).__name__

        if node_name not in ALLOWED_NODES:
            raise ValueError(
                f"SQL operation not allowed: {node_name}"
            )

        # CASE WHEN can contain an internal IF node.
        # Do not allow unrelated IF expressions.
        if isinstance(node, exp.If):
            if not isinstance(node.parent, exp.Case):
                raise ValueError(
                    "Standalone IF is not supported."
                )

    # 5. Restrict query to one table
    tables = list(tree.find_all(exp.Table))

    if len(tables) != 1:
        raise ValueError(
            "Exactly one approved table is required."
        )

    table = tables[0]

    if table.name.lower() not in ALLOWED_TABLES:
        raise ValueError(
            f"Table not allowed: {table.name}"
        )

    if table.catalog:
        raise ValueError(
            "Cross-database references are not allowed."
        )

    if table.db and table.db.lower() != "public":
        raise ValueError(
            "Only the public schema is allowed."
        )

    # No table aliases in this first version
    if table.alias:
        raise ValueError(
            "Table aliases are not supported in v1."
        )

    # 6. Validate column names
    aliases = {
        alias.alias.lower()
        for alias in tree.find_all(exp.Alias)
    }

    allowed_names = ALLOWED_COLUMNS | aliases

    for column in tree.find_all(exp.Column):

        column_name = column.name.lower()

        if column_name not in allowed_names:
            raise ValueError(
                f"Column not allowed: {column_name}"
            )

        if column.table and column.table.lower() != table.name.lower():
            raise ValueError(
                "Invalid table qualifier."
            )

        if column.db or column.catalog:
            raise ValueError(
                "Qualified column reference not allowed."
            )

    # 7. Convert parsed SQL back to PostgreSQL syntax
    try:
        validated_sql = tree.sql(
            dialect="postgres"
        )
    except Exception as error:
        raise ValueError(
            f"Failed to serialize SQL: {error}"
        ) from error

    return validated_sql
