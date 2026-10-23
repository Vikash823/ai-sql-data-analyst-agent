
from llm_service import generate_sql
from query_executor import execute_query


def main():

    print("\nAI SQL DATA ANALYST AGENT")
    print("---------------------------")

    while True:
        question = input("\nAsk a question (or exit): ")

        if question.strip().lower() == "exit":
            break

        if not question.strip():
            continue

        try:
            # Step 1: Generate SQL
            sql = generate_sql(question)

            print("\nGenerated SQL:")
            print(sql)

            # Step 2: Validate and execute
            columns, rows = execute_query(sql)

            # Step 3: Display results
            print("\nQUERY RESULTS")
            print("---------------------------")
            print(" | ".join(columns))

            for row in rows:
                print(" | ".join(str(value) for value in row))

            print(f"\nTotal rows: {len(rows)}")

        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()
