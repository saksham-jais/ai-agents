from agent import (
    apply_memory_action,
    decide_memory_action,
    generate_answer,
    retrieve_memory,
)


while True:
    user_message = input("\nYou: ").strip()
    if user_message.lower() == "exit":
        break
    if not user_message:
        continue

    decision = decide_memory_action(user_message)
    result = apply_memory_action(decision)
    print(f"[Memory action: {decision.action} - {result}]")

    memories = retrieve_memory(user_message)
    print("\n[Relevant memories]\n" + memories)

    answer = generate_answer(user_message, memories)
    print("\nAgent:", answer)
