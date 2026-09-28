from typing import Literal

from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    route: Literal["research", "code", "review", "finish"]
    reason: str = ""


class ReviewIssue(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    description: str
    recommendation: str


class ReviewReport(BaseModel):
    approved: bool
    summary: str
    issues: list[ReviewIssue] = Field(default_factory=list)


class CodeArtifact(BaseModel):
    files: dict[str, str] = Field(default_factory=dict)
    explanation: str = ""


class FinalResult(BaseModel):
    task: str
    status: Literal["completed", "failed"]
    project_path: str = ""
    files: list[str] = Field(default_factory=list)
    research: str = ""
    review: ReviewReport | None = None
    recommendations: str = ""
    iterations: int = 0
    memory_hits: list[str] = Field(default_factory=list)
    test_status: Literal["passed", "failed", "skipped"] = "skipped"
    test_output: str = ""