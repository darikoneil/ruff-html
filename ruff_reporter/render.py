from jinja2 import Environment, FileSystemLoader
from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime


if TYPE_CHECKING:
    from ruff_reporter.issues import IssueMapping
    from jinja2 import Environment



def render_source_files(issues_map: IssueMapping,
                        source_files: set[Path],
                        environment: Environment,
                        output_directory: Path) -> None:
    file_template = environment.get_template("file.html")
    # source_template = environment.get_template("source.html")
    # TODO: Implement source.html
    for file, issues in issues_map.iter("filename"):
        statistics = calculate_statistics(issues)
        rendered_file = file_template.render

            issues=issues,
            total_issues=len(issues),
            total_errors=sum(1 for issue in issues if issue.severity == "error"),
            total_warnings=sum(1 for issue in issues if issue.severity == "warning"),
            total_refactors=sum(1 for issue in issues if issue.severity == "refactor"),
            total_conventions=sum(1 for issue in issues if issue.severity == "convention"),
        )



if __name__ == "__main__":
    from ruff_reporter.issues import collect_issues
    from ruff_reporter.reporter import locate_source_files
    import json

    RESULTS_FILE = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\.ruff.json")
    OUTPUT_DIR = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\output")
    SOURCE_DIR = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\ruff_reporter")

    with open(RESULTS_FILE, "r") as file:
        ruff_report = json.load(file)

    issues_map = collect_issues(ruff_report)
    source_files = locate_source_files(SOURCE_DIR)

