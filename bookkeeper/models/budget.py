"""
Описан класс, представляющий бюджет
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Budget:
    """
    Бюджет
    """

    interval: str
    amount: float
    limit_amount: float
    pk: int = 0
