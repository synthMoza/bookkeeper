from PySide6 import QtWidgets, QtGui, QtCore
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.view.utility_widgets.table_widget import TableWidget


class ExpensesViewWidget(QtWidgets.QWidget):
    edit_expense_signal = QtCore.Signal(int)

    def __init__(self, categories_repo: AbstractRepository[Category], expenses_repo: AbstractRepository[Expense], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.expenses_repo = expenses_repo
        self.categories_repo = categories_repo

        self.text = "Последние расходы"
        self.label = QtWidgets.QLabel(self.text)
        self.labels = "Дата Сумма Категория Комментарий".split()
        self.expenses_table = TableWidget(0, 4, self.labels)
        self.expenses_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.expenses_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.expenses_table.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.expenses_table.customContextMenuRequested.connect(self.open_menu_callback)
        self.user_role = QtGui.Qt.ItemDataRole.UserRole

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.expenses_table)
        self.setLayout(self.layout)

    @QtCore.Slot()
    def update_expenses(self):
        last_count = 20
        all_expenses = self.expenses_repo.get_all()[:last_count]
        all_expenses.sort(key=lambda e: e.date, reverse=True)
        self.expenses_table.setRowCount(len(all_expenses))

        for row, expense in enumerate(all_expenses):
            columns = expense.get_rows(self.categories_repo)
            for i, elem in enumerate(columns):
                item = QtWidgets.QTableWidgetItem(elem)
                item.setData(self.user_role, expense.pk)
                self.expenses_table.setItem(row, i, item)

    def open_menu_callback(self, position):
        selected_indexes = self.expenses_table.selectedIndexes()
        if not selected_indexes:
            return

        menu = QtWidgets.QMenu()

        add_category_action = QtGui.QAction("Редактировать")
        add_category_action.triggered.connect(self.edit_expense_trigger)
        menu.addAction(add_category_action)

        remove_category_action = QtGui.QAction("Удалить")
        remove_category_action.triggered.connect(self.remove_expense_trigger)
        menu.addAction(remove_category_action)

        menu.exec_(self.expenses_table.viewport().mapToGlobal(position))

    def edit_expense_trigger(self):
        selected_indexes = self.expenses_table.selectedIndexes()
        index = selected_indexes[0]
        pk = index.data(self.user_role)
        self.edit_expense_signal.emit(pk)

    def remove_expense_trigger(self):
        selected_indexes = self.expenses_table.selectedIndexes()
        index = selected_indexes[0]
        pk = index.data(self.user_role)
        self.expenses_repo.delete(pk)
        self.update_expenses()
