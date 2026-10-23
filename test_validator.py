
from sql_validator import validate_sql


test_cases = [
    (
        "SELECT COUNT(*) FROM orders",
        True
    ),
    (
        "SELECT store_id, COUNT(*) FROM orders GROUP BY store_id",
        True
    ),
    (
        """SELECT store_id,
        COUNT(CASE WHEN order_status = 'REJECTED'
        THEN 1 END) * 100.0 /
        NULLIF(COUNT(order_id), 0) AS rejection_rate
        FROM orders
        GROUP BY store_id
        ORDER BY rejection_rate DESC
        LIMIT 3""",
        True
    ),
    (
        "DELETE FROM orders",
        False
    ),
    (
        "SELECT pg_sleep(10) FROM orders",
        False
    ),
    (
        "SELECT * FROM customers",
        False
    ),
    (
        "SELECT * FROM orders; DROP TABLE orders",
        False
    ),
]


for sql, should_pass in test_cases:
    try:
        result = validate_sql(sql)
        passed = should_pass
    except ValueError:
        passed = not should_pass

    print("PASS" if passed else "FAIL", "|", sql[:65])
