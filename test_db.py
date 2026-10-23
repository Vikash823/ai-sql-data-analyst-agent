
from db import get_connection


def test_database():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        store_id,
                        COUNT(*) AS total_orders
                    FROM orders
                    GROUP BY store_id
                    ORDER BY store_id;
                """)

                results = cursor.fetchall()

                print("DATABASE CONNECTION SUCCESSFUL\n")

                for store_id, total_orders in results:
                    print(
                        f"Store: {store_id} | "
                        f"Orders: {total_orders}"
                    )

    except Exception as error:
        print(f"Database Error: {error}")


if __name__ == "__main__":
    test_database()
