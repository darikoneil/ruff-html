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


def locate_linted_sources(search_dir: Path) -> set[Path]:
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
            for file in Path(source).rglob("*.py"):
                sources.add(file)
    return sources
