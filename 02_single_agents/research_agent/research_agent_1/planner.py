from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq


class ResearchTask(BaseModel):
	title: str = Field(description="Short name for the research task")
	query: str = Field(description="Specific web search query for the task")


class ResearchPlan(BaseModel):
	tasks: list[ResearchTask] = Field(
		min_length=3,
		max_length=3,
		description="Exactly three independent research tasks",
	)


def create_plan(llm: ChatGroq, topic: str) -> ResearchPlan:
	planner = llm.with_structured_output(ResearchPlan)
	response = planner.invoke(
		[
			HumanMessage(
				content=(
					f"Create exactly three independent research tasks for: {topic}. "
					"Cover fundamentals, practical applications, and limitations or "
					"tradeoffs. Each task must include a focused web search query."
				)
			)
		]
	)
	return response
