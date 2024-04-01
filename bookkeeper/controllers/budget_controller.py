from PySide6 import QtWidgets, QtCore

from bookkeeper.view.utility_widgets.table_widget import TableWidget
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense

import datetime


class BudgetController(QtCore.QObject):
    """
        Класс реализует паттерн Controller из архитектуры MVC для модели Budget
    """

    interval_column: int = 0
    sum_column: int = 1
    limit_sum_column: int = 2

    day_row: int = 0
    week_row: int = 1
    month_row: int = 2

    day_sum_default = 1000
    week_sum_default = 7000
    month_sum_default = 30000

    def __init__(self, expenses_repo: AbstractRepository[Expense], budget_repo: AbstractRepository[Budget]) -> None:
        super().__init__()
        self.budget_repo: AbstractRepository[Budget] = budget_repo
        self.expenses_repo: AbstractRepository[Expense] = expenses_repo
        self.model: TableWidget | None = None

    def set_model(self, model: TableWidget) -> None:
        """
        Установить соответствующую модель. Необходимо вынести в отдельную функцию, т.к. модели еще нет
        при инициализации контроллера
        """

        if not self.model:
            self.model: TableWidget = model

    def add_last_expenses(self, interval: str) -> None:
        """
        Найти затраты за выбранный временной промежуток

        Parameters
        ----------
        interval - временной промежуток ('day', 'week', 'month')

        Returns
        -------
        Список подходящих затрат
        """
        all_expenses = self.expenses_repo.get_all()
        last_expenses = []

        if interval == 'day':
            row = self.day_row
            russian_name = 'День'

            def comparator(x: datetime.datetime, y: datetime.datetime): return (x.year == y.year and x.month == y.month
                                                                                and x.day == y.day)
        elif interval == 'week':
            row = self.week_row
            russian_name = 'Неделя'

            def comparator(x: datetime.datetime, y: datetime.datetime): return (x.isocalendar().week ==
                                                                                y.isocalendar().week)
        elif interval == 'month':
            row = self.month_row
            russian_name = 'Месяц'

            def comparator(x: datetime.datetime, y: datetime.datetime): return x.year == y.year and x.month == y.month
        else:
            raise KeyError(f'unknown interval {interval}')

        current_date = datetime.datetime.today()
        for expense in all_expenses:
            if comparator(expense.date, current_date):
                last_expenses.append(expense)

        limit_amount = self.model.item(row, self.limit_sum_column).data(QtCore.Qt.ItemDataRole.UserRole)
        budget = Budget(russian_name, sum([e.amount for e in last_expenses]), limit_amount)
        self.budget_repo.add(budget)

    def update_budget_repo(self):
        self.add_last_expenses('day')
        self.add_last_expenses('week')
        self.add_last_expenses('month')

    def update_model(self):
        # First column - durations (day, week, month)
        item = QtWidgets.QTableWidgetItem('День')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
        self.model.setItem(self.day_row, self.interval_column, item)

        item = QtWidgets.QTableWidgetItem('Неделя')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
        self.model.setItem(self.week_row, self.interval_column, item)

        item = QtWidgets.QTableWidgetItem('Месяц')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
        self.model.setItem(self.month_row, self.interval_column, item)

        # Seconds column - aggregated expenses during given periods
        #self.budget_repo.get()

        # Third column - editable budget limits
        day_budget_item = QtWidgets.QTableWidgetItem('1000')
        day_budget_item.setData(QtCore.Qt.ItemDataRole.UserRole, 1000)
        day_budget_item.setFlags(day_budget_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.model.setItem(self.day_row, self.limit_sum_column, day_budget_item)

        week_budget_item = QtWidgets.QTableWidgetItem('7000')
        week_budget_item.setFlags(week_budget_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.model.setItem(self.week_row, self.limit_sum_column, week_budget_item)

        month_budget_item = QtWidgets.QTableWidgetItem('30000')
        month_budget_item.setFlags(month_budget_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.model.setItem(self.month_row, self.limit_sum_column, month_budget_item)
