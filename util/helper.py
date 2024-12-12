from datetime import datetime


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
