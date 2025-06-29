"""Utility functions for formatting numbers and currencies."""

from config.settings import CURRENCY_FORMAT, PERCENTAGE_FORMAT


def format_currency(value: float) -> str:
    """Format a number as currency."""
    return CURRENCY_FORMAT.format(value)


def format_percentage(value: float) -> str:
    """Format a number as percentage."""
    return PERCENTAGE_FORMAT.format(value)


def format_years_months(total_months: int) -> str:
    """Format total months as years and months."""
    years = total_months // 12
    months = total_months % 12
    return f"{years}Y {months}M"


def format_number(value: float, decimals: int = 0) -> str:
    """Format a number with thousand separators."""
    if decimals == 0:
        return f"{value:,.0f}"
    else:
        return f"{value:,.{decimals}f}"


def format_delta(value: float, prefix: str = "") -> str:
    """Format a delta value with + or - sign."""
    if value > 0:
        return f"{prefix}+{format_currency(value)}"
    elif value < 0:
        return f"{prefix}{format_currency(value)}"
    else:
        return f"{prefix}{format_currency(0)}" 