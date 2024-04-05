"""
Описан класс, представляющий расходную операцию
"""

from dataclasses import dataclass
from datetime import datetime

from typing import List
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.category import Category


@dataclass(slots=True)
class Expense:
    """
    Расходная операция.
    date - дата расхода
    amount - сумма расхода
    category_id - id категории расходов
    comment - комментарий к расходу
    pk - id записи в базе данных
    """
    date: datetime
    amount: float
    category_id: int
    comment: str = ''
    pk: int = 0

    def get_rows(self, repo: AbstractRepository[Category]) -> List[str]:
        """
        Получить текстовое описание расхода для вставки в таблицу
        в порядке "дата, сумма, категория, комментарий"
        в виде списка строк

        Parameters
        ----------
        repo - репозитория с категориями

        Returns
        -------
        Список с текстовым описанием класса
        """

        category = repo.get(self.category_id)

        if category is not None:
            return [
                self.date.strftime("%Y-%m-%d %H:%M:%S"),
                str(self.amount),
                category.name,
                self.comment,
            ]

        raise KeyError('no category_id in repo')

    @classmethod
    def delete_expenses_of_category(cls,
                                    repo: AbstractRepository['Expense'],
                                    category_id: int) -> None:
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
