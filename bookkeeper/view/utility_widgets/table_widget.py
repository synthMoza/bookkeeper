"""
Модуль с кастомным виджетом таблицы
"""

from typing import List, Any
from PySide6 import QtWidgets


class TableWidget(QtWidgets.QTableWidget):  # type: ignore
    """
    TableWidget адаптирует таблицу QTableWidget
    с необходимыми настройками (resize, selection mode)
    """
    def __init__(self, rows: int, columns: int, labels: List[str],
                 *args: Any, **kwargs: Any) -> None:
        super().__init__(rows, columns, *args, **kwargs)

        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setHorizontalHeaderLabels(labels)

        header = self.horizontalHeader()
        header.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().hide()
