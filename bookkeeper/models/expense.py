"""
Описан класс, представляющий расходную операцию
"""

from dataclasses import dataclass, field
from datetime import datetime

from typing import List
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.category import Category


@dataclass(slots=True)
class Expense:
    """
    Расходная операция.
    amount - сумма расхода
    category_id - id категории расходов
    date - дата расхода
    comment - комментарий к расходу
    pk - id записи в базе данных
    """
    date: datetime
    amount: float
    category_id: int
    comment: str = ''
    pk: int = 0

    def get_rows(self, repo: AbstractRepository['Category']) -> List[str]:
        """
        Получить текстовое описание расхода для вставки в таблицу в порядке "дата, сумма, категория, комментарий"
        в виде списка строк

        Parameters
        ----------
        repo - репозитория с категориями

        Returns
        -------
        Список с текстовым описанием класса
        """

        return [
            self.date.strftime("%Y-%m-%d %H:%M:%S"),
            str(self.amount),
            repo.get(self.category_id).name,
            self.comment,
        ]

    @classmethod
    def delete_expenses_of_category(cls, repo: AbstractRepository['Expense'], category_id: int):
        """
        Классовый метод для удаления конкретной категории из репозитория затрат

        Parameters
        ----------
        repo - репозитория с затратами
        category_id - id категории
        """

        expenses = repo.get_all({"category_id": category_id})
        for expense in expenses:
            repo.delete(expense.pk)
