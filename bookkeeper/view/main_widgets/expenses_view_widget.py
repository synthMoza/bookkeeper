"""
Модуль с описанием класса для отображения расходов
"""
from typing import Any

from PySide6 import QtWidgets, QtGui, QtCore
from bookkeeper.controllers.expenses_controller import ExpensesController  # type: ignore
from bookkeeper.view.utility_widgets.table_widget import TableWidget


class ExpensesViewWidget(QtWidgets.QWidget):  # type: ignore
    """
    Виджет отображения всех расходов в виде таблицы с возможностью
    удаления и редактирования расходов
    """

    edit_expense_signal = QtCore.Signal(int)

    def __init__(self, controller: ExpensesController, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.layout = QtWidgets.QVBoxLayout()

        self.text = "Последние расходы"
        self.label = QtWidgets.QLabel(self.text)
        self.labels = "Дата Сумма Категория Комментарий".split()
        self.expenses_table = TableWidget(0, 4, self.labels)
        self.expenses_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.expenses_table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.expenses_table.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.expenses_table.customContextMenuRequested.connect(
            self.open_menu_callback)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.expenses_table)
        self.setLayout(self.layout)

        self.controller.set_model(self.expenses_table)

    def open_menu_callback(self, position: QtCore.QPoint) -> None:
        """
        Триггер открытия меню при клике правой кнопки
        """

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

    def edit_expense_trigger(self) -> None:
        """
        Триггер редактирования траты при выборе соответствующего действия в меню
        """

        selected_indexes = self.expenses_table.selectedIndexes()
        index = selected_indexes[0]
        primary_key = index.data(QtGui.Qt.ItemDataRole.UserRole)
        self.edit_expense_signal.emit(primary_key)

    def remove_expense_trigger(self) -> None:
        """
        Триггер удаления траты при выборе соответствующего действия в меню
        """

        selected_indexes = self.expenses_table.selectedIndexes()
        index = selected_indexes[0]
        primary_key = index.data(QtGui.Qt.ItemDataRole.UserRole)

        self.controller.delete_expense(primary_key)
        self.controller.update_model()
