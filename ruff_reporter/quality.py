from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias

from ruff_reporter.issues import SEVERITY

if TYPE_CHECKING:
    from ruff_reporter.issues import Issue


__all__ = [
    "Statistics",
    "calculate_statistics",
]


"""
////////////////////////////////////////////////////////////////////////////////////////
// CODE SCORING
////////////////////////////////////////////////////////////////////////////////////////
"""


LetterGrade: TypeAlias = Literal[
    "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"
]


#: int: Scales the generated code score to not penalize large codebases.
_LINE_SCALING_FACTOR = 100


#: tuple[float, str]: Mapping of score to letter grade
GRADE_SCALE = (
    (97.0, "A+"),
    (93.0, "A"),
    (90.0, "A-"),
    (87.0, "B+"),
    (83.0, "B"),
    (80.0, "B-"),
    (77.0, "C+"),
    (73.0, "C"),
    (70.0, "C-"),
    (67.0, "D+"),
    (63.0, "D"),
    (60.0, "D-"),
)


def generate_score(
    lines: int, fixed: int, info: int, best_practice: int, warnings: int, errors: int
) -> float:
    """
    Score code quality using a weighted measure related the number of issues, their
    severity, and the size of the source code.

    :param lines: Number of lines in the source code
    :param fixed: Number of fixed issues
    :param info: Number of informational issues
    :param best_practice: Number of best practice issues
    :param warnings: Number of warning issues
    :param errors: Number of error issues
    :return: A score between 0 and 100
    """
    if sum((fixed, info, best_practice, warnings, errors)) == 0:
        return 100.0
    line_factor = lines / _LINE_SCALING_FACTOR
    unweighted_score = (
        errors * 16 + warnings * 8 + best_practice * 4 + info * 2 + fixed * 1
    )
    return 100.0 - (unweighted_score / line_factor)


def score_to_letter(
    score: float,
) -> LetterGrade:
    """
    Convert a code score to a letter grade.

    :param score: Code score
    :return Letter grade
    """
    for grade, letter in GRADE_SCALE:
        if score >= grade:
            # noinspection PyTypeChecker
            return letter
    return "F"


"""
////////////////////////////////////////////////////////////////////////////////////////
// STATISTICS
////////////////////////////////////////////////////////////////////////////////////////
"""


@dataclass(slots=True)
class Statistics:
    """
    Container for code quality statistics.

    :var lines: Number of lines in the source code
    :var issues: Number of issues
    :var fixed: Number of fixed issues
    :var info: Number of informational issues
    :var best_practice: Number of best practice issues
    :var warning: Number of warning issues
    :var error: Number of error issues
    :var grade: Letter grade
    :var score: Code score
    :var max_severity: Maximum severity of the issues
    """

    lines: int
    issues: int
    fixed: int
    info: int
    best_practice: int
    warning: int
    error: int
    grade: LetterGrade = "F"
    score: float = 0.0
    max_severity: SEVERITY = SEVERITY.NULL

    def __post_init__(self):
        """
        Calculate the code score and letter grade using the passed statistics.
        """
        self.score = generate_score(
            self.lines,
            self.fixed,
            self.info,
            self.best_practice,
            self.warning,
            self.error,
        )
        self.grade = score_to_letter(self.score)


def calculate_statistics(issues: set["Issue"], source_code: str) -> Statistics:
    """
    Calculate statistics for the given set of issues and source code.

    :param issues: Set of issues
    :param source_code: Source code
    :return: Statistics object
    """
    return Statistics(
        # count the last line, even if it's been formatted to be empty
        lines=source_code.count("\n") + 1,
        issues=len(issues),
        fixed=sum(1 for issue in issues if issue.severity == SEVERITY.FIXED),
        info=sum(1 for issue in issues if issue.severity == SEVERITY.INFO),
        best_practice=sum(
            1 for issue in issues if issue.severity == SEVERITY.BEST_PRACTICE
        ),
        warning=sum(1 for issue in issues if issue.severity == SEVERITY.WARNING),
        error=sum(1 for issue in issues if issue.severity == SEVERITY.ERROR),
        max_severity=max(
            (issue.severity for issue in issues), default=SEVERITY.NO_ISSUES
        ),
    )
