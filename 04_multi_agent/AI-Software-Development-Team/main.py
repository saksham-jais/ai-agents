import json

from supervisor import supervisor


task = input(
    "\nWhat software project should the team build?\n> "
)


result = supervisor(task)


print("\n")
print("=" * 60)
print("FINAL RESULT")
print("=" * 60)


print(json.dumps(result.model_dump(), indent=2))