import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent import run_task
from planner import create_plan


load_dotenv()


def synthesize_report(llm: ChatGroq, topic: str, results: list[str]) -> str:
	evidence = "\n\n".join(
		f"Task {index}:\n{result}" for index, result in enumerate(results, start=1)
	)
	response = llm.invoke(
		[
			HumanMessage(
				content=(
					f"Write a concise research report about: {topic}\n\n"
					f"Independent task results:\n{evidence}\n\n"
					"Synthesize the findings, compare agreements and disagreements, "
					"identify limitations, and finish with practical conclusions."
				)
			)
		]
	)
	return response.content


def research(topic: str) -> str:
	llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

	print("1. Planner: creating three tasks...")
	plan = create_plan(llm, topic)
	for index, task in enumerate(plan.tasks, start=1):
		print(f"   Task {index}: {task.title}")

	print("2. Agents: running tasks in parallel...")
	with ThreadPoolExecutor(max_workers=3) as executor:
		futures = [
			executor.submit(run_task, llm, task.title, task.query)
			for task in plan.tasks
		]
		results = [future.result() for future in futures]

	print("3. Synthesizer: creating final report...")
	report = synthesize_report(llm, topic, results)
	report_path = Path(__file__).resolve().parent / "research_report.md"
	report_path.write_text(report, encoding="utf-8")
	print(f"4. Report saved to {report_path}")
	return report


if __name__ == "__main__":
	topic = input("What would you like to research? ").strip()
	if not topic:
		raise SystemExit("A research topic is required.")
	print(research(topic))
