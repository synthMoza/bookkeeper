from PySide6 import QtWidgets


class ScrollableTextWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()

        self.text = "\n".join(f"text{i}" for i in range(0, 1000))
        self.label = QtWidgets.QLabel(self.text)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidget(self.label)

        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)
