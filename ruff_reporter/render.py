from pathlib import Path
from shutil import copy2

from jinja2 import Environment, FileSystemLoader

#
from ruff_reporter.issues import Issue, IssueMapping
from ruff_reporter.quality import Statistics, calculate_statistics

__all__ = [
    "render",
]


#: Names of required assets for the report.
_REQUIRED_ASSETS = ("styles.css",)


"""
////////////////////////////////////////////////////////////////////////////////////////
// MISC
////////////////////////////////////////////////////////////////////////////////////////
"""


def _collect_source_code(source_file: Path) -> str:
    """
    Collect the source code from a file.

    :param source_file: The file to collect the source code from.
    :return: The source code from the file.
    """
    with source_file.open("r") as file:
        return file.read()


def _copy_assets(output_directory: Path) -> None:
    """
    Copy the required assets to the output directory.

    :param output_directory: The directory to copy the assets to.
    """
    assets_directory = Path(__file__).parent.joinpath("templates", "assets")
    output_assets = output_directory.joinpath("assets")
    output_assets.mkdir(exist_ok=True, parents=True)
    for asset in _REQUIRED_ASSETS:
        try:
            asset_path = assets_directory.joinpath(asset)
            assert asset_path.exists()
        except AssertionError as exc:  # noqa: PERF203
            raise FileNotFoundError(
                f"Missing asset: {asset}. "
                f"Please re-install ruff-reporter or raise an "
                f"issue on the github repository"
            ) from exc
        else:
            copy2(assets_directory.joinpath(asset), output_assets)


def _match_abs_rel(
    abs_path: Path,
    paths: set[Path],
) -> Path:
    """
    Check if any path in a set of relative paths matches the given absolute path.

    :param abs_path: The path to check for.
    :param paths: The set of paths to check.
    :return: True if the set contains a path that matches the given path.
    """
    # Since we are using a set of a folder & file pair,
    # I don't ~think~ we need to worry about multiple matches
    # noinspection PyTypeChecker
    return next(
        (set_path for set_path in paths if abs_path.match(set_path)), abs_path.stem
    )


def _clean_relative_path(relative_path: Path) -> str:
    """
    Clean a relative path to use as a filename.

    :param relative_path: The path to clean.
    :return: The cleaned path.
    """
    # platform independent
    return str(relative_path).replace("\\", "/").replace("/", "-").replace(".py", "")


"""
////////////////////////////////////////////////////////////////////////////////////////
// RENDER FUNCS
////////////////////////////////////////////////////////////////////////////////////////
"""


def render_file_summary(
    environment: Environment,
    issues: set[Issue],
    statistics: Statistics,
    cleaned_relative_path: str,
    output_directory: Path,
):
    """
    Render a file summary.

    :param environment: The Jinja2 environment to use.
    :param issues: The issues to render.
    :param statistics: The statistics to render.
    :param cleaned_relative_path: The cleaned relative path to use.
    :param output_directory: The output directory to save the file to.
    """
    file_template = environment.get_template("file_summary.html")
    save_path = output_directory.joinpath(f"{cleaned_relative_path}-summary.html")
    issues = sorted(issues, key=lambda issue: issue.severity, reverse=True)
    rendered_summary = file_template.render(
        filename=cleaned_relative_path.replace("-", "/"),
        issues=issues,
        statistics=statistics,
    )
    with save_path.open("w") as file:
        file.write(rendered_summary)


def render_file_source(
    environment: Environment,
    issues: set[Issue],
    source_code: str,
    cleaned_relative_path: str,
    output_directory: Path,
):
    """
    Render a file source.

    :param environment: The Jinja2 environment to use.
    :param issues: The issues to render.
    :param source_code: The source code to render.
    :param cleaned_relative_path: The cleaned relative path to use.
    :param output_directory: The output directory to save the file to.
    """
    source_template = environment.get_template("file_source.html")
    save_path = output_directory.joinpath(f"{cleaned_relative_path}-source.html")
    rendered_source = source_template.render(
        filename=cleaned_relative_path.replace("-", "/"),
        issues=issues,
        source_code=source_code,
    )
    with save_path.open("w") as file:
        file.write(rendered_source)


def render_source_files(
    issues_map: IssueMapping,
    source_files: set[Path],
    environment: Environment,
    output_directory: Path,
) -> None:
    """
    Render the source files.

    :param issues_map: The issues map to render.
    :param source_files: The source files to render.
    :param environment: The Jinja2 environment to use.
    :param output_directory: The output directory to save the files to.
    """
    rendered_files = set()
    for absolute_path, issues in issues_map.iter("filename"):
        # I'd rather convert it here than in each downstream function or have to
        # convert Path <--> str in the IssueMapping / Issue
        absolute_path = Path(absolute_path)
        relative_path = _match_abs_rel(absolute_path, source_files)
        cleaned_relative_path = _clean_relative_path(relative_path)
        source_code = _collect_source_code(absolute_path)
        statistics = calculate_statistics(issues, source_code)
        render_file_summary(
            environment, issues, statistics, cleaned_relative_path, output_directory
        )
        render_file_source(
            environment, issues, source_code, cleaned_relative_path, output_directory
        )
        rendered_files.add(relative_path)

    perfect_files = source_files.difference(rendered_files)
    for file in perfect_files:
        statistics = calculate_statistics(set(), "")
        cleaned_relative_path = _clean_relative_path(file)
        render_file_summary(
            environment, set(), statistics, cleaned_relative_path, output_directory
        )


def render_severity_files(
    issues_map: IssueMapping,
    environment: Environment,
    output_directory: Path,
) -> None:
    severity_template = environment.get_template("severity.html")
    # TODO: Implement severity.html template
    for severity, issues in issues_map.iter("severity"):
        rendered_severity = severity_template.render(severity=severity, issues=issues)
        out_file = output_directory.joinpath(f"{severity}.html")
        with open(out_file, "w") as file:
            file.write(rendered_severity)


def render_ruleset_files(
    issues_map: IssueMapping,
    environment: Environment,
    output_directory: Path,
) -> None:
    # TODO: Implement ruleset.html template
    ruleset_template = environment.get_template("ruleset.html")
    for ruleset, issues in issues_map.iter("ruleset"):
        rendered_ruleset = ruleset_template.render(ruleset=ruleset, issues=issues)
        out_file = output_directory.joinpath(f"{ruleset}.html")
        with open(out_file, "w") as file:
            file.write(rendered_ruleset)


def render_all_file(
    issues_map: IssueMapping,
    environment: Environment,
    output_directory: Path,
) -> None:
    # TODO: Implement all.html template
    all_template = environment.get_template("all.html")
    rendered_all = all_template.render(issues=issues_map)
    out_file = output_directory.joinpath("all.html")
    with open(out_file, "w") as file:
        file.write(rendered_all)


def render_summary_file(
    issues_map: IssueMapping,
    environment: Environment,
    output_directory: Path,
) -> None:
    # TODO: Implement summary.html template
    summary_template = environment.get_template("summary.html")
    rendered_summary = summary_template.render(issues=issues_map)
    out_file = output_directory.joinpath("index.html")
    with open(out_file, "w") as file:
        file.write(rendered_summary)


"""
////////////////////////////////////////////////////////////////////////////////////////
// RENDER MAIN
////////////////////////////////////////////////////////////////////////////////////////
"""


def render(
    issues_map: IssueMapping,
    source_files: set[Path],
    output_directory: Path,
) -> None:
    template_directory = Path(__file__).parent.joinpath("templates")
    environment = Environment(loader=FileSystemLoader(str(template_directory)))
    _copy_assets(output_directory)
    render_source_files(issues_map, source_files, environment, output_directory)
    # render_severity_files(issues_map, environment, output_directory)
    # render_ruleset_files(issues_map, environment, output_directory)
    # render_all_file(issues_map, environment, output_directory)
    # render_summary_file(issues_map, environment, output_directory)
