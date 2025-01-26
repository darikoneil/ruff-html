import json
from pathlib import Path
from ruff_html.issues import IssueMapping, create_issue
from warnings import warn

__all__ = [
    "load_ruff_report",
]

"""
Functions for loading ruff's formatted output
"""


def collect_issues(ruff_report: list[dict]) -> IssueMapping:
    """
    Collects issues from a ruff report
    """
    issue_mapping = IssueMapping()
    issues = [create_issue(issue) for issue in ruff_report]
    for issue in issues:
        issue_mapping.add(issue)
    return issue_mapping


def locate_ruff_report() -> Path:
    """
    Locates the ruff linter's output file

    :raises: FileNotFoundError: If a ruff report is not found
    """
    current_dir = Path.cwd()
    files = (file for file in current_dir.glob("*ruff*.json"))

    # Only search recursively if we didn't find a file to avoid (potentially) searching
    # through a massive collection of files
    try:
        first_file = next(files)
    except StopIteration:
        files = (file for file in current_dir.rglob("*ruff*.json"))
        first_file = next(files, None)

    if first_file is None:
        raise FileNotFoundError(f"No ruff report found in {current_dir}")
    if next(files, None) is not None:
        warn(f"Multiple ruff reports found in {current_dir}, selected {first_file}")

    return first_file


def load_ruff_report(ruff_file: Path | None) -> IssueMapping:
    """
    Loads the a .json file containing the ruff linter's output
    """
    if ruff_file is None:
        ruff_file = locate_ruff_report()

    with open(ruff_file, "r") as file:
        report_data = json.load(file)

    return collect_issues(report_data)
