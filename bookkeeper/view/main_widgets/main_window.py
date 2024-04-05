"""
Модуль с описанием класса главного окна приложения
"""

from typing import Any

import sqlite3

from PySide6 import QtWidgets

from bookkeeper.view.main_widgets.expenses_view_widget import (
    ExpensesViewWidget)
from bookkeeper.view.main_widgets.expenses_add_widget import (
    ExpensesAddWidget)
from bookkeeper.view.main_widgets.budget_view_widget import (
    BudgetViewWidget)

from bookkeeper.controllers.categories_controller import (  # type: ignore
    CategoriesController)
from bookkeeper.controllers.expenses_controller import (  # type: ignore
    ExpensesController)
from bookkeeper.controllers.budget_controller import (  # type: ignore
    BudgetController)

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget


class MainWindow(QtWidgets.QWidget):  # type: ignore
    """
    Виджет главного окна инициализирует все базы данных, репозитории и виджеты
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # set up sqlite db and repos
        self.db_file = "book_keeper.db"
        self.create_categories_table()
        self.create_expenses_table()
        self.create_budget_table()

        self.categories_repository = SQLiteRepository(self.db_file, Category)
        self.expenses_repository = SQLiteRepository(self.db_file, Expense)
        self.budget_repository = SQLiteRepository(self.db_file, Budget)

        # controllers
        self.expenses_controller = ExpensesController(self.expenses_repository,
                                                      self.categories_repository)
        self.categories_controller = CategoriesController(self.categories_repository)
        self.budget_controller = BudgetController(self.expenses_repository,
                                                  self.budget_repository)

        # main widgets
        self.expenses_view_widget = ExpensesViewWidget(self.expenses_controller)
        self.budget_view_widget = BudgetViewWidget(self.budget_controller)
        self.expenses_add_widget = ExpensesAddWidget(self.expenses_controller,
                                                     self.categories_controller)

        # set up signals
        self.expenses_view_widget.edit_expense_signal.connect(
            self.expenses_add_widget.edit_expense)
        self.categories_controller.delete_expense_signal.connect(
            self.expenses_controller.delete_expenses_of_category)
        self.expenses_controller.update_budget_model_signal.connect(
            self.budget_controller.update_model)

        # initial trigger
        self.expenses_controller.update_model()

        # set up layouts
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.left_vertical_layout = QtWidgets.QVBoxLayout()
        self.right_vertical_layout = QtWidgets.QVBoxLayout()

        self.left_vertical_layout.addWidget(self.expenses_view_widget)
        self.left_vertical_layout.addWidget(self.budget_view_widget)
        self.right_vertical_layout.addWidget(self.expenses_add_widget)

        self.horizontal_layout.addLayout(self.left_vertical_layout)
        self.horizontal_layout.addLayout(self.right_vertical_layout)

        self.setLayout(self.horizontal_layout)

    def create_categories_table(self) -> None:
        """
        Инициализировать таблицу категорий
        """

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Category "
                "(pk INTEGER PRIMARY KEY, parent INTEGER, name TEXT)"
            )

    def create_expenses_table(self) -> None:
        """
        Инициализировать таблицу расходов
        """

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Expense "
                "(pk INTEGER PRIMARY KEY, amount REAL, category_id INTEGER, "
                "date DATETIME, comment TEXT,  FOREIGN KEY (category_id) "
                "REFERENCES Category(pk))"
            )

    def create_budget_table(self) -> None:
        """
        Инициализировать таблицу бюджетов
        """

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Budget "
                "(pk INTEGER PRIMARY KEY, interval TEXT, amount REAL, "
                "limit_amount REAL)"
            )
