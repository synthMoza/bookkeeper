"""
Описан класс, представляющий бюджет
"""

from dataclasses import dataclass
from typing import Literal
from datetime import datetime

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense


@dataclass(slots=True)
class Budget:
    """
    Модель бюджета хранит интервал ("День", "Неделя", "Месяц"),
    сумма затрат, лимит затрат на этот период и ключ pk
    """

    interval: Literal['День', 'Неделя', 'Месяц']
    amount: float
    limit_amount: float
    pk: int = 0

    def update_amount(self, repo: AbstractRepository[Expense]) -> None:
        """
        Обновить траты за выбранный интервал на основе репозитория затрат

        Parameters
        ----------
        repo - репозиторий с затратами
        """

        if self.interval == 'День':
            def comparator(x: datetime, y: datetime): return (x.year == y.year and x.month == y.month
                                                                                and x.day == y.day)
        elif self.interval == 'Неделя':
            def comparator(x: datetime, y: datetime): return (x.year == y.year and
                                                              x.isocalendar().week == y.isocalendar().week)
        elif self.interval == 'Месяц':
            def comparator(x: datetime, y: datetime): return x.year == y.year and x.month == y.month
        else:
            raise KeyError(f'unknown interval {self.interval}')

        current_date = datetime.today()
        all_expenses = repo.get_all()
        last_expenses = []
        for expense in all_expenses:
            if comparator(expense.date, current_date):
                last_expenses.append(expense)

        self.amount = sum([e.amount for e in last_expenses])
