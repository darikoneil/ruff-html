from typing import Literal, TYPE_CHECKING, TypeAlias
from dataclasses import dataclass

if TYPE_CHECKING:
    from ruff_reporter.issues import IssueMapping


LetterGrade: TypeAlias = Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"]

#: tuple[int, str]: Mapping of score to letter grade
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


def generate_score(issues_map: "IssueMapping") -> float:
    # max(0, 0 if fatal else 10.0 - ((float(5 * error + warning + refactor + convention)
    # / statement) * 10))
    ...


def score_to_letter(
    score: float,
) -> LetterGrade :
    for grade, letter in GRADE_SCALE:
        if score >= grade:
            # noinspection PyTypeChecker
            return letter
    return "F"


@dataclass(slots=True)
class Statistics:
    lines: int
    issues: int
    fixed: int
    info: int
    best_practice: int
    warning: int
    error: int
    grade: Literal
    score: float
