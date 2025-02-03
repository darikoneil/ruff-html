from pathlib import Path
import argparse
from warnings import warn


"""
////////////////////////////////////////////////////////////////////////////////////////
// LOCATE FILES
////////////////////////////////////////////////////////////////////////////////////////
"""



def _locate_file(search_dir: Path, tag: str) -> Path:
    """
    Internal method for locating files

    :param search_dir: Directory to conduct file search in
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
        raise FileNotFoundError(f"No {tag} file found in {search_dir}")
    if next(files, None) is not None:
        warn(f"Multiple {tag} files found in {search_dir}, selected {first_file}", stacklevel=2)

    return first_file


def locate_ruff_results(search_dir: Path) -> Path:
    """
    Locate the ruff linter's output file

    :param search_dir: The directory to search for the results file in
    :return: The path to the results file
    """
    return _locate_file(search_dir, "ruff.json")


def locate_output_directory(search_dir: Path) -> Path:
    """
    Locate the directory to output the report to

    :param search_dir: The directory to search for the output directory in
    :return: The path to the output directory
    """
    project_file = _locate_file(search_dir, "pyproject.toml")
    with open(project_file, "r") as file:
        lines = iter(file)
        for line in lines:
            if "ruff-report" in line:
                return Path(next(lines).split("=")[1].strip())
    output_directory = search_dir.joinpath("ruff-report")
    output_directory.mkdir(exist_ok=True)
    return output_directory


def locate_linted_source(search_dir: Path) -> set[Path]:
    """
    Locate the source file or directory that was linted

    :param search_dir: The directory to search for the source file or directory in
    :return: The path to the source file or directory
    """
    project_file = _locate_file(search_dir, "pyproject.toml")
    sources = set()
    with open(project_file, "r") as file:
        lines = iter(file)
        for line in lines:
            if "sources" in line:
                src_line = next(lines).split("=")[1].strip()
                sources.add(src_line)
                if "[" in src_line:
                    while "]" not in (src_line := next(lines)):
                        sources.add(src_line.replace(",", "").strip())
    if len(sources) == 0:
        with open(project_file, "r") as file:
            lines = iter(file)
            for line in lines:
                if "name" in line:
                    sources.add(line.split("=")[1].strip())

    for source in sources:
        if Path(source).is_dir():
            source.add
    if sources:
    return None


"""
////////////////////////////////////////////////////////////////////////////////////////
// REPORTER MAIN
////////////////////////////////////////////////////////////////////////////////////////
"""


def reporter(results_file: Path,
             output_directory: Path,
             linted: Path | None = None
             ) -> None:
    """
    Main function for the reporter

    :param results_file: The path to the ruff results file
    :param output_directory: The directory to output the report to
    :param linted: The path to the linted file or directory
    """




if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Generate a report from ruff's linter output")
    arg_parser.add_argument("-source",
                            "-s",
                            required=False,
                            default=".",
                            type=str,
                            help="The directory of the project containing the source-files and ruff results")
    args = arg_parser.parse_args()

    source_directory_ = Path(args.source).absolute()
    results_file_ = locate_ruff_results(source_directory_)
    output_directory_ = locate_output_directory(source_directory_)
    linted_source = locate_linted_source(source_directory_)

