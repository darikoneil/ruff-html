from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from ruff_reporter.issue import IssuesMap

#: tuple[int, str]: Mapping of score to letter grade
LETTER_GRADES = (
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


def generate_score(issues_map: "IssuesMap") -> float:
    # max(0, 0 if fatal else 10.0 - ((float(5 * error + warning + refactor + convention)
    # / statement) * 10))
    ...


def score_to_letter(
    score: float,
) -> Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"]:
    for grade, letter in LETTER_GRADES:
        if score >= grade:
            # noinspection PyTypeChecker
            return letter
    return "F"
