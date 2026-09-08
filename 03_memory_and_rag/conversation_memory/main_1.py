from agent_1 import remember_and_answer


while True:

    user_message = input("\nYou: ")

    if user_message.lower() == "exit":
        break

    response, decision, memory_saved = remember_and_answer(user_message)

    if memory_saved:
        print("\n[Memory saved]")

    print("\nAgent:", response)