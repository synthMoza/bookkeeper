# type: ignore
from PySide6 import QtWidgets, QtCore

from bookkeeper.view.utility_widgets.table_widget import TableWidget
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense


class BudgetController(QtCore.QObject):
    """
        Класс реализует паттерн Controller из архитектуры MVC для модели Budget
    """

    day_sum_default = 1000
    week_sum_default = 7000
    month_sum_default = 30000

    def __init__(self, expenses_repo: AbstractRepository[Expense],
                 budget_repo: AbstractRepository[Budget]) -> None:
        super().__init__()
        self.expenses_repo: AbstractRepository[Expense] = (
            expenses_repo)
        self.budget_repo = budget_repo
        self.model: TableWidget | None = None

    def set_model(self, model: TableWidget) -> None:
        """
        Установить соответствующую модель. Необходимо вынести
        в отдельную функцию, т.к. модели еще нет
        при инициализации контроллера
        """

        if not self.model:
            self.model = model

    def init_model(self) -> None:
        budgets = [
            Budget('День', 0, self.day_sum_default),
            Budget('Неделя', 0, self.week_sum_default),
            Budget('Месяц', 0, self.month_sum_default),
        ]

        for budget in budgets:
            self.budget_repo.add(budget)

        self.update_model()
        self.model.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.model.cellChanged.connect(self.cell_changed_callback)

    def cell_changed_callback(self):
        day_limit_amount_item = self.model.item(0, 2)
        week_limit_amount_item = self.model.item(1, 2)
        month_limit_amount_item = self.model.item(2, 2)

        day_budget = self.budget_repo.get(
            day_limit_amount_item.data(QtCore.Qt.ItemDataRole.UserRole))
        week_budget = self.budget_repo.get(
            week_limit_amount_item.data(QtCore.Qt.ItemDataRole.UserRole))
        month_budget = self.budget_repo.get(
            month_limit_amount_item.data(QtCore.Qt.ItemDataRole.UserRole))

        day_budget.limit_amount = float(day_limit_amount_item.text())
        week_budget.limit_amount = float(week_limit_amount_item.text())
        month_budget.limit_amount = float(month_limit_amount_item.text())

        self.budget_repo.update(day_budget)
        self.budget_repo.update(week_budget)
        self.budget_repo.update(month_budget)

    def update_model(self):
        budgets = self.budget_repo.get_all()
        for budget in budgets:
            budget.update_amount(self.expenses_repo)

        for i, budget in enumerate(budgets):
            self.budget_repo.update(budget)

            item = QtWidgets.QTableWidgetItem(budget.interval)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, budget.pk)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.model.setItem(i, 0, item)

            amount_item = QtWidgets.QTableWidgetItem(str(budget.amount))
            amount_item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            amount_item.setData(QtCore.Qt.ItemDataRole.UserRole, budget.pk)
            self.model.setItem(i, 1, amount_item)

            limit_amount_item = QtWidgets.QTableWidgetItem(str(budget.limit_amount))
            limit_amount_item.setData(QtCore.Qt.ItemDataRole.UserRole, budget.pk)
            limit_amount_item.setData(QtCore.Qt.ItemDataRole.UserRole, budget.pk)
            self.model.setItem(i, 2, limit_amount_item)
