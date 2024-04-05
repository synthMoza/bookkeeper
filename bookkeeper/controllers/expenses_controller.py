# type: ignore
from PySide6 import QtWidgets, QtGui, QtCore

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.view.utility_widgets.table_widget import TableWidget


class ExpensesController(QtCore.QObject):
    """
        Класс реализует паттерн Controller из архитектуры MVC для модели Expense
    """

    update_budget_model_signal = QtCore.Signal()

    def __init__(self, expenses_repo: AbstractRepository[Expense],
                 categories_repo: AbstractRepository[Category]) -> None:
        super().__init__()
        self.expenses_repo = expenses_repo
        self.categories_repo = categories_repo
        self.model = None

    def set_model(self, model: TableWidget) -> None:
        """
        Установить соответствующую модель. Необходимо вынести
        в отдельную функцию, т.к. модели еще нет
        при инициализации контроллера
        """

        if not self.model:
            self.model = model

    def get_expense(self, pk: int) -> Expense | None:
        """
        Получить расход по ключу

        Parameters
        ----------
        pk - ключ расхода

        Returns
        -------
        Expense или None, если расхода с таким ключом нет
        """

        return self.expenses_repo.get(pk)

    def add_expense(self, e: Expense) -> None:
        """
        Добавить новую затрату в репозиторий. Если она уже существует,
        то она не обновится.

        Parameters
        ----------
        e - новая затрата
        """

        self.expenses_repo.add(e)

    def update_expense(self, e: Expense) -> None:
        """
        Добавить новую затрату в репозиторий. Если она еще не существует в репозитории,
        то она не добавится в него.

        Parameters
        ----------
        e - обновленная затрата
        """

        self.expenses_repo.update(e)

    def update_model(self) -> None:
        """
        Обновить внутреннюю модель значениями затрат из репозитория.
        """

        last_count = 20
        all_expenses = self.expenses_repo.get_all()[:last_count]
        all_expenses.sort(key=lambda e: e.date, reverse=True)
        self.model.setRowCount(len(all_expenses))

        for row, expense in enumerate(all_expenses):
            columns = expense.get_rows(self.categories_repo)
            for i, elem in enumerate(columns):
                item = QtWidgets.QTableWidgetItem(elem)
                item.setData(QtGui.Qt.ItemDataRole.UserRole, expense.pk)
                self.model.setItem(row, i, item)

        self.update_budget_model_signal.emit()

    def delete_expense(self, pk: int) -> None:
        """
        Удалить затрату из репозитория

        Parameters
        ----------
        pk - ключ затраты из репозитория
        """
        try:
            self.expenses_repo.delete(pk)
        except KeyError:
            pass

    def delete_expenses_of_category(self, category_id: int) -> None:
        """
        Удалить затраты выбранной категории из репозитория

        Parameters
        ----------
        category_id - ключ категории
        """

        Expense.delete_expenses_of_category(self.expenses_repo, category_id)
