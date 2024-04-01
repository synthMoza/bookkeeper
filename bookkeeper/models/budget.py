"""
Описан класс, представляющий бюджет
"""

from dataclasses import dataclass, field
from datetime import timedelta
from bookkeeper.models.category import Category


@dataclass(slots=True)
class Expense:
    """
    Бюджет
    """
    duration: timedelta
    sum: float
    pk: int
