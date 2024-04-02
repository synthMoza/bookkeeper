from PySide6 import QtWidgets, QtCore

from bookkeeper.controllers.budget_controller import BudgetController
from bookkeeper.view.utility_widgets.table_widget import TableWidget


class BudgetViewWidget(QtWidgets.QWidget):
    def __init__(self, budget_controller: BudgetController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.controller = budget_controller

        self.text = "Бюджет"
        self.label = QtWidgets.QLabel(self.text)

        self.labels = ["", "Сумма", "Бюджет"]
        self.budget_table = TableWidget(3, 3, self.labels)
        self.budget_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.budget_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.budget_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.budget_table)
        self.setLayout(self.layout)

        self.controller.set_model(self.budget_table)
        self.controller.init_model()

