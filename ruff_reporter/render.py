from pathlib import Path
from shutil import copy2

from jinja2 import Environment, FileSystemLoader

#
from ruff_reporter.issues import IssueMapping
from ruff_reporter.quality import calculate_statistics

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


def collect_source_code(source_file: Path) -> str:
    """
    Collect the source code from a file.

    :param source_file: The file to collect the source code from.
    :return: The source code from the file.
    """
    with open(source_file) as file:
        return file.read()


def copy_assets(output_directory: Path) -> None:
    """
    Copy the required assets to the output directory.

    :param output_directory: The directory to copy the assets to.
    """
    assets_directory = Path(__file__).parent.joinpath("templates", "assets")
    output_assets = output_directory.joinpath("templates/assets")
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


def short_set_of_paths_match(abs_path: Path, paths: set[Path], ) -> Path:
    """
    Check if any path in a set of relative paths matches the given absolute path.

    :param abs_path: The path to check for.
    :param paths: The set of paths to check.
    :return: True if the set contains a path that matches the given path.
    """
    # Since we are using a set of a folder & file pair,
    # I don't ~think~ we need to worry about multiple matches
    # noinspection PyTypeChecker
    return next((set_path for set_path in paths if abs_path.match(set_path)),
                abs_path.stem)


def clean_path(path: Path) -> str:
    """
    Clean a path for display.

    :param path: The path to clean.
    :return: The cleaned path.
    """
    # platform independent
    return str(path).replace("\\", "/").replace("/", "-")


"""
////////////////////////////////////////////////////////////////////////////////////////
// RENDER FUNCS
////////////////////////////////////////////////////////////////////////////////////////
"""


def render_source_files(
    issues_map: IssueMapping,
    source_files: set[Path],
    environment: Environment,
    output_directory: Path,
) -> None:
    # TODO: Implement source.html template
    file_template = environment.get_template("file_summary.html")
    source_template = environment.get_template("file_source.html")
    rendered_files = set()

    for source_file, issues in issues_map.iter("filename"):
        source_file = Path(source_file)
        cleaned_name = short_set_of_paths_match(source_file, source_files)
        source_code = collect_source_code(source_file)
        statistics = calculate_statistics(issues, source_code)
        sum_out_file = output_directory.joinpath(f"{clean_path(cleaned_name)}-summary.html")
        src_out_file = output_directory.joinpath(f"{clean_path(cleaned_name)}-source.html")
        rendered_summary = file_template.render(
            filename=cleaned_name, issues=issues, statistics=statistics
        )
        with open(sum_out_file, "w") as file:
            file.write(rendered_summary)

        rendered_source = ""
        with open(src_out_file, "w") as file:
            file.write(rendered_source)

        rendered_files.add(source_file)

    clean_files = source_files.difference(rendered_files)
    for file in clean_files:
        sum_out_file = output_directory.joinpath(f"{file.stem}-summary.html")
        rendered_summary = file_template.render(
            filename=file.stem, issues=set(), statistics=calculate_statistics(set(), "")
        )
        # noinspection PyAssignmentToLoopOrWithParameter
        with open(sum_out_file, "w") as file:
            file.write(rendered_summary)


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
    copy_assets(output_directory)
    render_source_files(issues_map, source_files, environment, output_directory)
    # render_severity_files(issues_map, environment, output_directory)
    # render_ruleset_files(issues_map, environment, output_directory)
    # render_all_file(issues_map, environment, output_directory)
    # render_summary_file(issues_map, environment, output_directory)
