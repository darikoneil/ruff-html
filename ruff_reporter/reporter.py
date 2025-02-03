from pathlib import Path
from re import search


"""
////////////////////////////////////////////////////////////////////////////////////////
// LOCATE FILES
////////////////////////////////////////////////////////////////////////////////////////
"""


def _locate_file(search_dir: Path, tag: str) -> Path:
    """
    Internal method for locating files

    :param search_dir: Dir
    """
    # Only search recursively if we didn't find a file to avoid (potentially) searching
    # through a massive collection of files
    files = (file for file in search_dir.glob(f"*{tag}*"))
    try:
        first_file = next(files)
    except StopIteration:
        files = (file for file in search_dir.rglob("*ruff*.json"))
        first_file = next(files, None)

    if first_file is None:
        raise FileNotFoundError(f"No ruff report found in {search_dir}")
    if next(files, None) is not None:
        warn(f"Multiple ruff reports found in {search_dir}, selected {first_file}")

    return first_fil



def locate_project_file(search_dir: Path) -> Path | None:
    project_file = next(search_dir.glob("pyproject.toml"))

    return project_file


def locate_configuration(search_dir: Path) -> Path:
    """
    Locate the ruff linter's configuration file

    :param search_dir: The directory to search for the configuration file in
    :return: The path to the configuration file
    """
    ...


def locate_results(search_dir: Path) -> Path:
    """
    Locate the ruff linter's output file

    :param search_dir: The directory to search for the results file in
    :return: The path to the results file
    """
    ...


def locate_source_files(search_dir: Path) -> set[Path]:
    """
    Locates all source files in the given directory

    :param search_dir: The path to the source code
    :return: A set of paths to the source files
    """
    return set(search_dir.rglob("*.py"))


def locate_files(project_dir: str):
    project_dir = Path(project_dir)



"""
////////////////////////////////////////////////////////////////////////////////////////
// REPORTER MAIN
////////////////////////////////////////////////////////////////////////////////////////
"""


def reporter():
    ...
