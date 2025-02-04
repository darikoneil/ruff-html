from pathlib import Path
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
        files = (file for file in search_dir.rglob(f"*{tag}"))
        first_file = next(files, None)

    if first_file is None:
        raise FileNotFoundError(f"No {tag} file found in {search_dir}")
    if next(files, None) is not None:
        warn(
            f"Multiple {tag} files found in {search_dir}, selected {first_file}",
            stacklevel=2,
        )

    return first_file


def locate_source_files(search_dir: Path | set[Path]) -> set[Path]:
    if isinstance(search_dir, set):
        return {file for directory in search_dir for file in locate_source_files(directory)}
    else:
        return {file for file in search_dir.rglob("*.py")}
