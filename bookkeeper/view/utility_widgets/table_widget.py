from PySide6 import QtWidgets


class TableWidget(QtWidgets.QTableWidget):
    def __init__(self, rows, columns, labels, *args, **kwargs):
        super().__init__(rows, columns, *args, **kwargs)

        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setHorizontalHeaderLabels(labels)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().hide()
