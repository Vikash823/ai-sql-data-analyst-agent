
from llm_service import generate_sql


def main():
    print("\nAI SQL AGENT - STEP 3")
    print("----------------------")

    while True:
        question = input("\nEnter your question (or exit): ")

        if question.lower().strip() == "exit":
            break

        if not question.strip():
            continue

        try:
            sql = generate_sql(question)

            print("\nGenerated SQL:")
            print(sql)

        except Exception as error:
            print(f"\nLLM Error: {error}")


if __name__ == "__main__":
    main()
