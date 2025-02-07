from pathlib import Path
from warnings import warn

__all__ = [
    "locate_source_files",
]


"""
////////////////////////////////////////////////////////////////////////////////////////
// LOCATE FILES
////////////////////////////////////////////////////////////////////////////////////////
"""


def _locate_file(search_dir: Path, tag: str) -> Path:
    """
    Internal method for locating files

    :param search_dir: Directory to conduct file search in
    :param tag: Tag to search for
    :return: Path to file
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
        msg = f"No {tag} file found in {search_dir}"
        raise FileNotFoundError(msg)
    if next(files, None) is not None:
        warn(
            f"Multiple {tag} files found in {search_dir}, selected {first_file}",
            stacklevel=2,
        )

    return first_file


def locate_source_files(search_dir: Path | tuple[Path]) -> set[Path]:
    """
    Locate source files in the given directory or set of directories.

    :param search_dir: The directory or directories to search for source files.
    :return: A set of source files.
    """
    # Files are returned as relative to the search directory's parent to ensure that
    # names are interpretable while identical files in different modules are distinct.
    if isinstance(search_dir, tuple):
        return {
            file for directory in search_dir for file in locate_source_files(directory)
        }
    return {file.relative_to(search_dir.parent) for file in search_dir.rglob("*.py")}
