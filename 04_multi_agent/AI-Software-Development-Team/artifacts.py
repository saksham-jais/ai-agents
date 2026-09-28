from pathlib import Path
import subprocess
import sys

from models import CodeArtifact


def write_artifact(artifact: CodeArtifact, destination: Path) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for filename, content in artifact.files.items():
        relative_path = Path(filename)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"Unsafe generated path: {filename}")
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(relative_path.as_posix())
    return written


def run_generated_tests(destination: Path) -> tuple[str, str]:
    test_files = list(destination.rglob("test_*.py")) + list(destination.rglob("*_test.py"))
    if not test_files:
        return "skipped", "No generated test files found."
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(destination)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    return ("passed" if result.returncode == 0 else "failed"), output