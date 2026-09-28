from pathlib import Path

from artifacts import run_generated_tests, write_artifact
from config import structured_invoke
from memory_store import remember, search
from models import CodeArtifact, FinalResult, ReviewReport, RouteDecision
from coder import coder_agent
from researcher import researcher_agent
from reviewer import reviewer_agent


MAX_ITERATIONS = 5
PROJECTS_DIR = Path(__file__).resolve().parent / "generated_projects"


def choose_route(
    task: str,
    research: str,
    artifact: CodeArtifact | None,
    review: ReviewReport | None,
    iteration: int,
) -> RouteDecision:
    if not research:
        return RouteDecision(route="research", reason="Research is missing")
    if artifact is None:
        return RouteDecision(route="code", reason="No implementation exists")
    if review is None:
        return RouteDecision(route="review", reason="Implementation needs review")
    if review.approved or iteration >= MAX_ITERATIONS:
        return RouteDecision(route="finish", reason="Review is approved or budget is exhausted")

    decision = structured_invoke(
        RouteDecision,
        f"""You supervise a software project.
Task: {task}
Current iteration: {iteration}/{MAX_ITERATIONS}
Review: {review.model_dump_json()}
Choose code to revise the implementation or finish if further changes are not useful.""",
    )
    return decision if decision.route in {"code", "finish"} else RouteDecision(route="code")


def supervisor(task: str) -> FinalResult:
    research = ""
    artifact = None
    review = None
    iteration = 0
    memory_hits = search(task)
    memory_context = "\n".join(item["outcome"] for item in memory_hits)

    while iteration < MAX_ITERATIONS:
        route = choose_route(task, research, artifact, review, iteration)
        print(f"\nSUPERVISOR -> {route.route.upper()}: {route.reason}")
        if route.route == "research":
            research = researcher_agent(task, memory_context)
        elif route.route == "code":
            feedback = review.model_dump_json() if review else ""
            artifact = coder_agent(task, research, artifact, feedback)
        elif route.route == "review":
            review = reviewer_agent(task, artifact)
        else:
            break
        iteration += 1

    if artifact is None:
        return FinalResult(task=task, status="failed", iterations=iteration)

    project_path = PROJECTS_DIR / f"project_{iteration}"
    files = write_artifact(artifact, project_path)
    test_status, test_output = run_generated_tests(project_path)
    remember(task, artifact.explanation)
    recommendations = (
        "Approved by reviewer."
        if review and review.approved
        else "Review budget exhausted; inspect remaining issues before deployment."
    )
    return FinalResult(
        task=task,
        status="completed",
        project_path=str(project_path),
        files=files,
        research=research,
        review=review,
        recommendations=recommendations,
        iterations=iteration,
        memory_hits=[item["outcome"] for item in memory_hits],
        test_status=test_status,
        test_output=test_output,
    )
