"""
Описан класс, представляющий расходную операцию
"""

from dataclasses import dataclass, field
from datetime import datetime

from typing import List
from bookkeeper.repository.abstract_repository import AbstractRepository


@dataclass(slots=True)
class Expense:
    """
    Расходная операция.
    amount - сумма
    category_id - id категории расходов
    date - дата расхода
    comment - комментарий
    pk - id записи в базе данных
    """
    date: datetime
    amount: float
    category_id: int
    comment: str = ''
    pk: int = 0

    def get_rows(self, repo: AbstractRepository['Expense']) -> List[str]:
        return [
            self.date.strftime("%Y-%m-%d %H:%M:%S"),
            str(self.amount),
            repo.get(self.category_id).name,
            self.comment,
        ]

    @classmethod
    def delete_expenses_of_category(cls, repo: AbstractRepository['Expense'], category_id: int):
        expenses = repo.get_all({"category_id": category_id})
        for expense in expenses:
            repo.delete(expense.pk)
        self.categories_repo.get_all()
