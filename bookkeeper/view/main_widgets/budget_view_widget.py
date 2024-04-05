"""
Модуль с описанием виджета для отображения бюджета
"""

from typing import Any
from PySide6 import QtWidgets

from bookkeeper.controllers.budget_controller import BudgetController  # type: ignore
from bookkeeper.view.utility_widgets.table_widget import TableWidget


class BudgetViewWidget(QtWidgets.QWidget):  # type: ignore
    """
    Виджет отображения бюджетов на день, неделю и месяц с
    возможностью редактирования лимитов
    """

    def __init__(self, budget_controller: BudgetController, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.controller = budget_controller

        self.text = "Бюджет"
        self.label = QtWidgets.QLabel(self.text)

        self.labels = ["", "Сумма", "Бюджет"]
        self.budget_table = TableWidget(3, 3, self.labels)

        header = self.budget_table.horizontalHeader()
        header.setSectionResizeMode(0,
                                    QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1,
                                    QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2,
                                    QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.budget_table)
        self.setLayout(self.layout)

        self.controller.set_model(self.budget_table)
        self.controller.init_model()
