from collections.abc import Generator, ValuesView
from dataclasses import dataclass
from enum import IntEnum
from functools import cached_property
from typing import Any, Literal, TypeAlias
from warnings import warn

__all__ = [
    "SEVERITY",
    "Filter",
    "Filtered_Issues",
    "Issue",
    "IssueMapping",
    "collect_issues",
]


"""
////////////////////////////////////////////////////////////////////////////////////////
// RULESET SEVERITY
////////////////////////////////////////////////////////////////////////////////////////
"""


class SEVERITY(IntEnum):
    """
    Severity levels for detected issues.

    :var NULL: No severity level
    :var NO_ISSUES: No issues
    :var FIXED: Automatically fixed
    :var INFO: Informational message
    :var BEST_PRACTICE: Best practices or conventions
    :var WARNING: Warning
    :var ERROR: Error
    """

    # These are ordered in powers of 2 to allow for weighted comparisons
    #: Unable to identify severity level
    NULL = -1
    #: No issues
    NO_ISSUES = 0
    #: Automatically fixed
    FIXED = 1
    #: Documentation or informational message
    INFO = 2
    #: Best practices or conventions
    BEST_PRACTICE = 3
    #: Warning
    WARNING = 4
    #: Error
    ERROR = 5


class RULESETS:
    """
    Namespace containing rulesets and their respective severity levels
    """

    # This is basically just a dictionary under the hood with dot notation. I won't
    # ever need to iterate through values and have cached the keys. I'm just choosing
    # this option for explicitness (vs subclassing a dictionary) and to have the
    # the container and the match method in the same place (vs making a simplenamespace
    # or dict & a method). Ideally this wouldn't need instantiation, but I'm not sure
    # cache the keys without having to manually do enter them. I am not a compiler :/
    #: PyFlakes ruleset
    F: SEVERITY = SEVERITY.ERROR
    #: Pycodestyle
    E: SEVERITY = SEVERITY.ERROR
    W: SEVERITY = SEVERITY.WARNING
    #: McCabe complexity
    C: SEVERITY = SEVERITY.BEST_PRACTICE
    #: iSort
    I: SEVERITY = SEVERITY.BEST_PRACTICE
    #: PEP8 Naming
    N: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Pydocstyle
    D: SEVERITY = SEVERITY.INFO
    #: Pyupgrade
    U: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-2020
    YTT: SEVERITY = SEVERITY.WARNING
    #: flake8-annotations
    ANN: SEVERITY = SEVERITY.INFO
    #: flake8-async
    ASYNC: SEVERITY = SEVERITY.WARNING
    #: flake8-bandit
    S: SEVERITY = SEVERITY.WARNING
    #: flake8-blind-except
    BLE: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-boolean-trap
    FBT: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-bugbear
    B: SEVERITY = SEVERITY.WARNING
    #: flake8-builtins
    A: SEVERITY = SEVERITY.ERROR
    #: flake8-commas
    COM: SEVERITY = SEVERITY.INFO
    #: flake8-comprehensions
    COMP: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-datetimez
    DTZ: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-debugger
    T10: SEVERITY = SEVERITY.ERROR
    #: flake8-django
    DJ: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-errmsg
    EM: SEVERITY = SEVERITY.WARNING
    #: flake8-executable
    EXE: SEVERITY = SEVERITY.WARNING
    #: flake8-future-annotations
    FA: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-implicit-str-concat
    ISC: SEVERITY = SEVERITY.WARNING
    #: flake8-import-conventions
    ICN: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-logging
    LOG: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-logging-format
    G: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-no-pep420
    INP: SEVERITY = SEVERITY.ERROR
    #: flake8-pie
    PIE: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-print
    T20: SEVERITY = SEVERITY.ERROR
    #: flake8-pyi
    PYI: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-pytest-style
    PT: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-quotes
    Q: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-raise
    RSE: SEVERITY = SEVERITY.WARNING
    #: flake8-return
    RET: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-self
    SLF: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-slots
    SLOT: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-simplify
    SIM: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-tidy-imports
    TID: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-type-checking
    TC: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-gettext
    INT: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-unused-arguments
    ARG: SEVERITY = SEVERITY.WARNING
    #: flake8-use-pathlib
    PTH: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flake8-todos
    TD: SEVERITY = SEVERITY.WARNING
    #: flake8-fixme
    FIX: SEVERITY = SEVERITY.WARNING
    #: eradicate
    ERA: SEVERITY = SEVERITY.WARNING
    #: pandas-vet
    PD: SEVERITY = SEVERITY.BEST_PRACTICE
    #: pygrep-hooks
    PGH: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Pylint
    PL: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Convention
    PLC: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Error
    PLE: SEVERITY = SEVERITY.ERROR
    #: Refactor
    R: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Warning
    PLW: SEVERITY = SEVERITY.WARNING
    #: tryceratops
    TRY: SEVERITY = SEVERITY.BEST_PRACTICE
    #: flynt
    FLY: SEVERITY = SEVERITY.BEST_PRACTICE
    #: NumPy-specific rules
    NPY: SEVERITY = SEVERITY.BEST_PRACTICE
    #: FastAPI
    FAST: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Airflow
    AIR: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Perflint
    PERF: SEVERITY = SEVERITY.BEST_PRACTICE
    #: refurb
    FURB: SEVERITY = SEVERITY.BEST_PRACTICE
    #: pydoclint
    DOC: SEVERITY = SEVERITY.BEST_PRACTICE
    #: Ruff-specific rules
    RUF: SEVERITY = SEVERITY.BEST_PRACTICE

    @cached_property
    def keys(self) -> set:
        """
        Get the keys of the rulesets
        """
        return {key for key in dir(self) if "__" not in key} | {"get", "keys", "match"}

    def get(self, key: str) -> SEVERITY:
        """
        Get the severity level of a rule.

        :param key: The rule to get the severity level of
        :return: The severity level of the rule
        """
        # I don't care I touch the magics
        return RULESETS.__dict__.get(self.match(key), SEVERITY.NULL)

    def match(self, issue_code: str) -> str | None:
        """
        Get the ruleset for a given code
        """
        for length in range(3, 0, -1):
            prefix = issue_code[:length]
            if prefix in self.keys:
                return prefix
        warn(f"Unable to identify ruleset for {issue_code}", stacklevel=3)


#: For caching purposes
_RULESETS = RULESETS()


def get_severity(issue_code: str) -> SEVERITY:
    """
    Get the severity level of a rule.

    :param issue_code: The rule to get the severity level of
    :return: The severity level of the rule
    """
    return _RULESETS.get(issue_code)


"""
////////////////////////////////////////////////////////////////////////////////////////
// REPRESENTING ISSUES
////////////////////////////////////////////////////////////////////////////////////////
"""


@dataclass(slots=True)
class Location:
    """
    Represents a location in a file

    :var column: The column number
    :var row: The row number
    """

    #: column: The column number
    column: int
    #: row: The row number
    row: int

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (self.column, self.row) == (other.column, other.row)
        return False

    def __hash__(self) -> int:
        return hash((self.column, self.row))


@dataclass(slots=True)
class Edits:
    """
    Represents the edits conducted by a fix

    :var content: The content of the edit
    :var end_location: The end location of the edit
    :var location: The location of the edit
    """

    #: content: The content of the edit
    content: str
    #: end_location: The end location of the edit
    end_location: Location
    #: location: The location of the edit
    location: Location

    def __post_init__(self):
        # noinspection PyArgumentList
        self.end_location = Location(**self.end_location)
        # noinspection PyArgumentList
        self.location = Location(**self.location)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (
                self.content,
                self.end_location.__hash__(),
                self.location.__hash__(),
            ) == (
                other.content,
                other.end_location.__hash__(),
                other.location.__hash__(),
            )
        return False

    def __hash__(self) -> int:
        return hash(
            (self.content, self.end_location.__hash__(), self.location.__hash__())
        )


@dataclass(slots=True)
class Fix:
    """
    Represents an automatic fix

    :var applicability: The applicability of the fix
    :var edits: The edits conducted by the fix
    :var message: The message of the fix
    """

    #: applicability: The applicability of the fix
    applicability: Literal["safe", "unsafe"]
    #: edits: The edits conducted by the fix
    edits: Edits
    #: message: The message of the fix
    message: str

    def __post_init__(self):
        # noinspection PyArgumentList,PyUnresolvedReferences
        self.edits = Edits(**self.edits[0])

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (self.applicability, self.edits.__hash__(), self.message) == (
                other.applicability,
                other.edits.__hash__(),
                other.message,
            )
        return False

    def __hash__(self) -> int:
        return hash((self.applicability, self.edits.__hash__(), self.message))


@dataclass(slots=True)
class Issue:
    """
    Represents an issue detected by the ruff linter

    :var cell: The cell field
    :var code: The issue's code
    :var end_location: The issue's end location
    :var filename: The file the issue was detected in
    :var fix: Information containing automatic fixes
    :var location: The issue's location
    :var message: The issue's message
    :var noqa_row: The noqa row
    :var url: A URL to the issue's documentation
    :var severity: The issue's severity
    """

    # "cell" field that I do not understand the purpose of...
    cell: Any | None
    #: str: The issue's code
    code: str
    #: end_location: The issue's end location
    end_location: Location
    #: filename: The file the issue was detected in
    filename: str
    #: fix: Information containing automatic fixes
    fix: Fix | None
    #: location: The issue's location
    location: Location
    #: message: The issue's message
    message: str
    #: no quality field
    noqa_row: int | None
    #: url: A URL to the issue's documentation
    url: str | None
    #: severity: The issue's severity
    severity: SEVERITY

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (
                self.cell,
                self.code,
                self.end_location.__hash__(),
                self.filename,
                self.fix,
                self.location.__hash__(),
                self.message,
                self.noqa_row,
                self.url,
                self.severity,
            ) == (
                other.cell,
                other.code,
                other.end_location.__hash__(),
                other.filename,
                other.fix,
                other.location.__hash__(),
                other.message,
                other.noqa_row,
                other.url,
                other.severity,
            )
        return False

    def __hash__(self) -> int:
        return hash(
            (
                self.cell,
                self.code,
                self.end_location.__hash__(),
                self.filename,
                self.fix,
                self.location.__hash__(),
                self.message,
                self.noqa_row,
                self.url,
                self.severity,
            )
        )


"""
////////////////////////////////////////////////////////////////////////////////////////
// ISSUE MAPPING
////////////////////////////////////////////////////////////////////////////////////////
"""


def create_issue(serialized_issue: dict) -> Issue:
    """
    Create an Issue object from a dictionary.

    :param serialized_issue: The dictionary to create the issue from
    :return: The created issue
    """
    return Issue(
        cell=serialized_issue.get("cell"),  # for safety, I don't know what this is
        code=serialized_issue["code"],
        end_location=Location(**serialized_issue["end_location"]),
        filename=serialized_issue["filename"],
        fix=Fix(**serialized_issue["fix"])
        if serialized_issue.get("fix") is not None
        else None,
        location=Location(**serialized_issue["location"]),
        message=serialized_issue["message"],
        noqa_row=serialized_issue.get("noqa_row"),
        url=serialized_issue["url"],
        severity=get_severity(serialized_issue["code"]),
    )


Filter: TypeAlias = Literal["filename", "ruleset", "code", "severity", "fix"]


Filtered_Issues: TypeAlias = set["Issue"]


class IssueMapping:
    """
    A many-key to one-value mapping of issues allowing for retrieval by filename,
    ruleset, code, severity, and fixes.
    """

    def __init__(self) -> None:
        """
        Initialize the issue mapping
        """
        #: the actual issues
        self._values: dict[int, Issue] = {}
        #: keys map to sets of hashes pointing to included issues
        self._file_map: dict[str, set[int]] = {}
        self._ruleset_map: dict[str, set[int]] = {}
        self._code_map: dict[str, set[int]] = {}
        self._severity_map: dict[str, set[int]] = {}
        self._fix_map: dict[str, set[int]] = {}

    @staticmethod
    def _add_to_map(mapping, key, value) -> None:
        """
        Add a value to a mapping (in-place)

        :param mapping: The mapping to add to
        :param key: The key to add to
        :param value: The value to add
        """
        if key not in mapping:
            mapping[key] = set()
        mapping[key].add(value)

    def add(self, issue: Issue) -> None:
        """
        Add an issue to the mapping.

        :param issue: The issue to add
        """
        issue_key = id(issue)
        self._values[issue_key] = issue
        self._add_to_map(self._file_map, issue.filename, issue_key)
        self._add_to_map(self._ruleset_map, _RULESETS.match(issue.code), issue_key)
        self._add_to_map(self._code_map, issue.code, issue_key)
        self._add_to_map(self._severity_map, issue.severity.name, issue_key)
        if issue.fix is not None:
            self._add_to_map(self._fix_map, issue.fix, issue_key)

    def get(self, key: str, issue_filter: Filter | None = None) -> Filtered_Issues:
        """
        Get issues from the mapping.

        :param key: The key to retrieve
        :param issue_filter: The filter to apply
        :return: The issues
        """
        if filter is None:
            return self._retrieve_issues(key, self._values)
        # noinspection PyTypeChecker
        return self._retrieve_issues(key, self._match_filter(issue_filter))

    def values(self) -> ValuesView[Issue]:
        """
        Get all issues in the mapping
        """
        return self._values.values()

    def iter(self, issue_filter: Filter) -> Generator[tuple[str, set[Issue]]]:
        """
        Iterate through all issues in the filtered mapping

        :param issue_filter: The filter to apply
        :return: The issues
        """
        issue_map = self._match_filter(issue_filter)
        semantic_keys = issue_map.keys()
        return ((key, self._retrieve_issues(key, issue_map)) for key in semantic_keys)

    def _retrieve_issues(self, key: str, inner_map: dict) -> set[Issue]:
        """
        Retrieve issues from a mapping.

        :param key: The key to retrieve
        :param inner_map: The inner map to retrieve from
        :return: The issue or issues
        """
        return {self._values[hash_key] for hash_key in inner_map.get(key, set())}

    def _match_filter(self, issue_filter: Filter) -> dict:
        """
        Match a filter to the appropriate mapping

        :param issue_filter: The filter to match
        :return: The matched mapping
        """
        match issue_filter:
            case "filename":
                return self._file_map
            case "ruleset":
                return self._ruleset_map
            case "code":
                return self._code_map
            case "severity":
                return self._severity_map
            case "fix":
                return self._fix_map
            case _:
                raise ValueError(f"Invalid filter: {issue_filter}")


def collect_issues(ruff_file: list[dict]) -> IssueMapping:
    """
    Collects issues from a ruff output .json file.

    :param ruff_file: The ruff report to collect issues from
    :return: The collected issues
    """
    issue_mapping = IssueMapping()
    for issue in ruff_file:
        issue_mapping.add(create_issue(issue))
    return issue_mapping
