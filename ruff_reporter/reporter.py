from pathlib import Path
import json
from ruff_reporter.issues import collect_issues
from jinja2 import Environment, FileSystemLoader
from ruff_reporter.render import render_source_files
from ruff_reporter.search import locate_source_files

RUFF_FILE = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\.ruff.json")
OUTPUT_DIR = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\output")
SOURCE_DIR = Path(R"C:\Users\Yuste\PycharmProjects\ruff-reporter\ruff_reporter")

#: Path to the templates directory
_TEMPLATE_DIR = Path(__file__).parent.joinpath("templates")


"""
////////////////////////////////////////////////////////////////////////////////////////
// REPORTER MAIN
////////////////////////////////////////////////////////////////////////////////////////
"""


def reporter() -> None:
    # First load the ruff results.
    # Next collect source files.
    # Finally render the report.

    # TEMPORARY
    ruff_file = RUFF_FILE
    output_directory = OUTPUT_DIR
    source_directories = {SOURCE_DIR}
    # TODO: Implement as arguments or infer.

    with open(ruff_file, "r") as file:
        ruff_issues = json.load(file)

    issues_map = collect_issues(ruff_issues)
    source_files = locate_source_files(source_directories)
    environment = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)))

    render_source_files(issues_map,
                        source_files,
                        environment,
                        output_directory)


if __name__ == "__main__":
    reporter()
