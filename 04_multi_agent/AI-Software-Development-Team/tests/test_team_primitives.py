import tempfile
import unittest
from pathlib import Path

from artifacts import write_artifact
from models import CodeArtifact, ReviewReport, RouteDecision
from supervisor import choose_route


class TeamPrimitiveTests(unittest.TestCase):
    def test_artifact_writer_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = CodeArtifact(files={"../escape.py": "bad"})
            with self.assertRaises(ValueError):
                write_artifact(artifact, Path(directory))

    def test_route_requires_research_before_code(self):
        route = choose_route("build an API", "", None, None, 0)
        self.assertEqual(route.route, "research")

    def test_route_requires_review_before_finish(self):
        artifact = CodeArtifact(files={"main.py": "print('ok')"})
        route = choose_route("build an API", "findings", artifact, None, 2)
        self.assertEqual(route.route, "review")

    def test_approved_review_finishes(self):
        artifact = CodeArtifact(files={"main.py": "print('ok')"})
        review = ReviewReport(approved=True, summary="Looks good")
        route = choose_route("build an API", "findings", artifact, review, 3)
        self.assertEqual(route.route, "finish")


if __name__ == "__main__":
    unittest.main()