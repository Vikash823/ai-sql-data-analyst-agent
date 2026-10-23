from sql_validator import validate_sql

sql = """
SELECT
    COUNT(*) FILTER (
        WHERE order_status = 'REJECTED'
    ) AS rejected_orders
FROM orders
"""

try:
    validated_sql = validate_sql(sql)
    print("VALIDATION PASSED")
    print(validated_sql)

except ValueError as error:
    print("VALIDATION FAILED:", error)