from jinja2 import Environment, FileSystemLoader
from typing import TYPE_CHECKING
from pathlib import Path
from importlib_metadata import version
from typing import TypedDict
from datetime import datetime
from ruff_report.issues import SEVERITY

if TYPE_CHECKING:
    from ruff_report.issue import IssuesMap


__all__ = [
    "render_template",
]


#: Default path to the templates directory
_DEFAULT_TEMPLATE_PATH = Path(R"/ruff_report\templates")

#: Default path to the output file
_TEMP_OUTPUT_PATH = Path(R"./outputs")
_TEMP_OUTPUT_PATH.mkdir(exist_ok=True)


def render_template(
    issues_map: "IssuesMap",
    output_path: Path = _TEMP_OUTPUT_PATH,
    template_path: Path = _DEFAULT_TEMPLATE_PATH,
):
    env = Environment(loader=FileSystemLoader(str(_DEFAULT_TEMPLATE_PATH)))
    template = env.get_template("index.html")
    statistics = {
        "total_files": issues_map.get_total_files(),
        "total_issues": issues_map.get_total_issues(),
        "total_fixed": issues_map.get_total_fixed(),
        "total_errors": issues_map.get_total_errors(),
        "highest_severity": issues_map.get_highest_severity(),
    }
    rendered_html = template.render(
        issues_map=issues_map,
        render_data=datetime.today().strftime("%H:%M:%S, %m-%d-%Y"),
        statistics=statistics,
    )

    with open(output_path.joinpath("index.html"), "w") as file:
        file.write(rendered_html)
