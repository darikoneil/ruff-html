from ruff_report.load import load_ruff_report
from ruff_report.render import render_template


def hooker():
    issues_map = load_ruff_report(ruff_file=None)
    render_template(issues_map)


if __name__ == "__main__":
    hooker()
