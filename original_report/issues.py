from enum import IntEnum
from dataclasses import dataclass
from sys import maxsize
from typing import Any, Literal, TypeAlias, Iterable, ValuesView
from pathlib import Path
from functools import singledispatchmethod
from functools import cached_property, lru_cache
from warnings import warn


__all__ = [
    "IssueMapping",
    "create_issue",
]


"""
Implementation for representing issues detected by the ruff linter.
"""


Filter: TypeAlias = Literal["filename", "ruleset", "code", "severity", "fix"]


Filtered_Issues: TypeAlias = set["Issue"] | list[set["Issue"]]


class SEVERITY(IntEnum):
    """
    Severity levels for detected issues.

    :var NULL: No severity level
    :var FIXED: Automatically fixed
    :var INFO: Informational message
    :var BEST_PRACTICE: Best practices or conventions
    :var WARNING: Warning
    :var ERROR: Error
    """

    #: Unable to identify severity level
    NULL = -1
    #: Automatically fixed
    FIXED = 0
    #: Documentation or informational message
    INFO = 1
    #: Best practices or conventions
    BEST_PRACTICE = 2
    #: Warning
    WARNING = 3
    #: Error
    ERROR = 4


class RULESETS:
    """
    Namespace containing rulesets and their respective severity levels
    """

    # This is basically just a dictionary under the hood with dot notation. I won't
    # ever need to iterate through values, so just choosing a nice explicit option.
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


@dataclass(slots=True)
class Location:
    """
    Represents a location in a file

    @var column: The column number
    @var row: The row number
    """

    #: column: The column number
    column: int
    #: row: The row number
    row: int

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return (self.column, self.row) == (other.column, other.row)
        else:
            return False

    def __hash__(self) -> int:
        return hash((self.column, self.row))


@dataclass(slots=True)
class Edits:
    """
    Represents the edits conducted by a fix

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

    def __eq__(self, other: Any) -> bool:
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
        else:
            return False

    def __hash__(self) -> int:
        return hash(
            (self.content, self.end_location.__hash__(), self.location.__hash__())
        )


@dataclass(slots=True)
class Fix:
    """
    Represents an automatic fix

    """

    #: applicability: The applicability of the fix
    applicability: Literal["safe", "unsafe"]
    #: edits: The edits conducted by the fix
    edits: Edits
    #: message: The message of the fix
    message: str

    def __post_init__(self):
        # noinspection PyArgumentList
        self.edits = Edits(**self.edits[0])

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return (self.applicability, self.edits.__hash__(), self.message) == (
                other.applicability,
                other.edits.__hash__(),
                other.message,
            )
        else:
            return False

    def __hash__(self) -> int:
        return hash((self.applicability, self.edits.__hash__(), self.message))


@dataclass(slots=True)
class Issue:
    """
    Represents an issue detected by the ruff linter
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

    def __eq__(self, other: Any) -> bool:
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
        else:
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


def create_issue(serialized_issue: dict) -> Issue:
    """
    Create an Issue object from a dictionary.
    """
    return Issue(
        cell=serialized_issue.get(
            "cell", None
        ),  # for safety, I don't know what this is
        code=serialized_issue["code"],
        end_location=Location(**serialized_issue["end_location"]),
        filename=Path(serialized_issue["filename"]).stem,
        fix=Fix(**serialized_issue["fix"])
        if serialized_issue.get("fix") is not None
        else None,
        location=Location(**serialized_issue["location"]),
        message=serialized_issue["message"],
        noqa_row=serialized_issue.get("noqa_row", None),
        url=serialized_issue["url"],
        severity=get_severity(serialized_issue["code"]),
    )


class IssueMapping:
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
        """
        if key not in mapping:
            mapping[key] = set()
        mapping[key].add(value)

    @staticmethod
    def _retrieve_issues(key, inner_map: dict) -> set[Issue]:
        """
        Retrieve issues from a mapping.

        :param key: The key to retrieve
        :param inner_map: The inner map to retrieve from
        :return: The issue or issues
        """
        if isinstance(key, str):
            return inner_map.get(key, set())
        elif isinstance(key, Iterable):
            return set.intersection(*(inner_map.get(k, set()) for k in key))
        else:
            raise TypeError(f"Invalid key type: {type(key)}")

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

    @singledispatchmethod
    def get(
        self, issue_filters: Filter | Iterable[Filter], key: str | list
    ) -> Filtered_Issues:
        raise TypeError(f"Invalid filter type: {type(issue_filters)}")

    @get.register(str)
    def get_one_filter(
        self, issue_filters: Filter, key: str | list[str]
    ) -> Filtered_Issues:
        """
        Get an issue from the mapping.

        :param issue_filters: The filters to apply
        :param key: The key to get
        :return: The issue or issues
        """
        match issue_filters:
            case "filename":
                return self._retrieve_issues(key, self._file_map)
            case "ruleset":
                return self._retrieve_issues(key, self._ruleset_map)
            case "code":
                return self._retrieve_issues(key, self._ruleset_map)
            case "severity":
                return self._retrieve_issues(key, self._severity_map)
            case "fix":
                return self._retrieve_issues(key, self._fix_map)
            case _:
                raise ValueError(f"Invalid filter: {issue_filters}")

    @get.register(list)
    def get_multiple_filters(
        self, issue_filters: list[Filter], key: str
    ) -> Filtered_Issues:
        """
        Get an issue from the mapping.

        :param issue_filters: The filters to apply
        :param key: The key to get
        :return: The issue or issues
        """
        return [self.get_one_filter(filter_, key) for filter_ in issue_filters]

    def get_all(self) -> ValuesView[Issue]:
        """
        Get all issues in the mapping
        """
        return self._values.values()

    @lru_cache(maxsize=1)
    def get_total_issues(self) -> int:
        """
        Get the total number of issues in a mapping.

        :return: The total number of issues
        """
        return len(self.get_all())

    @lru_cache(maxsize=1)
    def get_total_files(self) -> int:
        """
        Get the total number of files in a mapping.

        :return: The total number of files
        """
        return len(self._file_map.keys())

    @lru_cache(maxsize=1)
    def get_total_errors(self) -> int:
        """
        Get the total number of errors
        """
        return len(self.get("severity", SEVERITY.ERROR.name))

    @lru_cache(maxsize=1)
    def get_total_warnings(self) -> int:
        """
        Get the total number of warnings
        """
        return len(self.get("severity", SEVERITY.WARNING.name))

    @lru_cache(maxsize=1)
    def get_total_best_practices(self) -> int:
        """
        Get the total number of best practices
        """
        return len(self.get("severity", SEVERITY.BEST_PRACTICE.name))

    @lru_cache(maxsize=1)
    def get_total_info(self) -> int:
        """
        Get the total number of informational messages
        """
        return len(self.get("severity", SEVERITY.INFO.name))

    @lru_cache(maxsize=1)
    def get_total_fixed(self) -> int:
        """
        Get the total number of fixed issues
        """
        return len(self._fix_map.values())

    @lru_cache(maxsize=1)
    def get_highest_severity(self) -> str:
        """
        Get the highest severity level
        """
        max_security = max(
            (SEVERITY[key] for key in self._severity_map.keys()), default=SEVERITY.NULL
        )
        return max_security.name
