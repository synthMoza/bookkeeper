from PySide6 import QtWidgets, QtCore

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.view.utility_widgets.table_widget import TableWidget
from bookkeeper.models.expense import Expense


class BudgetViewWidget(QtWidgets.QWidget):
    def __init__(self, expenses_repo: AbstractRepository[Expense], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.repo = expenses_repo

        self.text = "Бюджет"
        self.label = QtWidgets.QLabel(self.text)

        self.labels = ["", "Сумма", "Бюджет"]
        self.budget_table = TableWidget(3, 3, self.labels)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.budget_table)
        self.setLayout(self.layout)

        self.update_budget()

    def update_budget(self):
        item = QtWidgets.QTableWidgetItem('День')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
        self.budget_table.setItem(0, 0, item)

        item = QtWidgets.QTableWidgetItem('Неделя')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
        self.budget_table.setItem(1, 0, item)

        item = QtWidgets.QTableWidgetItem('Месяц')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
        self.budget_table.setItem(2, 0, item)

        all_expenses = self.repo.get_all()
        #day_expenses = sum([expense.amount for expense in all_expenses if expense.])

        day_budget_item = QtWidgets.QTableWidgetItem('1000')
        day_budget_item.setFlags(day_budget_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.budget_table.setItem(0, 2, day_budget_item)

        week_budget_item = QtWidgets.QTableWidgetItem('7000')
        week_budget_item.setFlags(week_budget_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.budget_table.setItem(1, 2, week_budget_item)

        month_budget_item = QtWidgets.QTableWidgetItem('30000')
        month_budget_item.setFlags(month_budget_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.budget_table.setItem(2, 2, month_budget_item)
