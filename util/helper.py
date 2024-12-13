import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def create_date_from_month_year(year: int, month: int) -> str:
    """
    Creates an ISO 8601 string representing the first day of the given month and year.
    Format: YYYY-MM-DDT00:00:00
    """
    return datetime(year, month, 1).isoformat()


def create_date_from_year(year: int) -> str:
    """
    Creates an ISO 8601 string representing the first day of the year.
    Format: YYYY-MM-DD
    """
    return datetime(year, 1, 1).isoformat()


def assert_true(expected, actual) -> None:
    """
    Custom assertion function that raises a specific exception when `expected` is not equal to `actual`

    Args:
        expected: expected value
        actual: actual value
    """
    if not (expected == actual):
        raise AssertionError(f"Assertion failed on condition: {expected} != {actual}")


def from_str_to_enum(enum_class, label: str):
    label_upper = label.strip().upper()
    if label_upper in enum_class.__members__:
        return enum_class[label_upper]
    else:
        raise NotImplementedError(f"{label_upper} text is not in valid enums: {enum_class.__members__}!")
