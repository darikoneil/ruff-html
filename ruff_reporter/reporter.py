import json
from pathlib import Path

from ruff_reporter.issues import collect_issues
from ruff_reporter.render import render
from ruff_reporter.search import locate_source_files

__all__ = [
    "reporter",
]


"""
////////////////////////////////////////////////////////////////////////////////////////
// REPORTER MAIN
////////////////////////////////////////////////////////////////////////////////////////
"""


def reporter() -> None:
    """
    Main function for ruff-reporter. This function will load the ruff results,
    organize the issues into a many-key to one-value mapping, collect the source files,
    and render the report.
    """
    ruff_file = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\.ruff.json")
    output_directory = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\output")
    source_directories = (
        Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\ruff_reporter"),
    )
    # TODO: Implement as arguments or infer.

    with open(ruff_file) as file:
        ruff_issues = json.load(file)

    issues_map = collect_issues(ruff_issues)
    source_files = locate_source_files(source_directories)

    if output_directory.exists():
        for file in output_directory.rglob("*"):
            if file.is_file():
                file.unlink()
    else:
        output_directory.mkdir(exist_ok=True, parents=True)

    render(issues_map, source_files, output_directory)


if __name__ == "__main__":
    reporter()
