import asyncio

from agents import (
    security_agent,
    performance_agent,
    architecture_agent,
    synthesis_agent
)


async def run_system(code):

    # -------------------------
    # FAN-OUT
    # -------------------------

    results = await asyncio.gather(

        security_agent(code),

        performance_agent(code),

        architecture_agent(code)

    )

    # -------------------------
    # FAN-IN
    # -------------------------

    final_result = await synthesis_agent(
        code,
        results
    )

    return final_result


async def main():

    code = """
def calculate_total(items):

    total = 0

    for item in items:
        total += item["price"]

    return total
"""

    result = await run_system(code)

    print("\n==============================")
    print("FINAL ENGINEERING REVIEW")
    print("==============================\n")

    print(result)


if __name__ == "__main__":

    asyncio.run(main())