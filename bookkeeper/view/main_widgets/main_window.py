import sqlite3

from PySide6 import QtWidgets

from bookkeeper.view.main_widgets.expenses_view_widget import ExpensesViewWidget
from bookkeeper.view.main_widgets.expenses_add_widget import ExpensesAddWidget
from bookkeeper.view.main_widgets.budget_view_widget import BudgetViewWidget
from bookkeeper.utils import read_tree

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set up sqlite db and repos
        self.db_file = "book_keeper.db"
        self.create_categories_table()
        self.create_expenses_table()

        self.categories_repository = SQLiteRepository(self.db_file, Category)
        self.expenses_repository = SQLiteRepository(self.db_file, Expense)

        # main widgets
        self.expenses_view_widget = ExpensesViewWidget(self.categories_repository, self.expenses_repository)
        self.budget_view_widget = BudgetViewWidget(self.expenses_repository)
        self.expenses_add_widget = ExpensesAddWidget(self.categories_repository, self.expenses_repository)

        # set up signals
        self.expenses_add_widget.update_expenses_signal.connect(self.expenses_view_widget.update_expenses)
        self.expenses_view_widget.edit_expense_signal.connect(self.expenses_add_widget.edit_expense)

        # initial trigger
        self.expenses_add_widget.update_expenses()

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

    def create_categories_table(self):
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Category "
                "(pk INTEGER PRIMARY KEY, parent INTEGER, name TEXT)"
            )

    def create_expenses_table(self):
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Expense "
                "(pk INTEGER PRIMARY KEY, amount REAL, category_id INTEGER, "
                "date DATETIME, comment TEXT,  FOREIGN KEY (category_id) REFERENCES Category(pk))"
            )
