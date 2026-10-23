
from agent_graph_v2 import agent


def main():

    print("\nAI SQL AGENT - TOOL CALLING VERSION")
    print("-----------------------------------")

    while True:

        question = input(
            "\nAsk a question (or exit): "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        try:
            result = agent.invoke({
                "question": question,
                "attempts": 0,
                "error": "",
                "result": {}
            })

            print("\nFINAL RESULT")
            print("--------------------------")
            print(result["answer"])

        except Exception as error:
            print(f"\nAgent error: {error}")


if __name__ == "__main__":
    main()
