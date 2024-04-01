from datetime import datetime

from PySide6 import QtWidgets
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QDoubleValidator


class LabeledInput(QtWidgets.QWidget):
    def __init__(self, text, placeholder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.input = QtWidgets.QLineEdit(placeholder)

        # without the label it will be just an input window
        if text:
            self.label = QtWidgets.QLabel(text)
            self.layout.addWidget(self.label)

        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

    def get_text(self):
        return self.input.text()

    def set_placeholder(self, placeholder: str):
        self.input.clear()
        self.input.insert(placeholder)


class LabeledFloatInput(LabeledInput):
    def __init__(self, text, placeholder, *args, **kwargs):
        super().__init__(text, placeholder, *args, **kwargs)
        self.input.setValidator(QDoubleValidator(self.input))


class LabeledDateInput(QtWidgets.QWidget):
    def __init__(self, text, placeholder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()

        if text:
            self.label = QtWidgets.QLabel(text)
            self.layout.addWidget(self.label)

        self.input = QtWidgets.QDateTimeEdit()
        self.qt_format = "yyyy-MM-dd hh:mm:ss"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

        self.input.setDisplayFormat(self.qt_format)
        self.input.setDateTime(QDateTime.currentDateTime())
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

    def get_datetime(self) -> datetime:
        return datetime.strptime(self.input.dateTime().toString(self.qt_format), self.datetime_format)


class LabeledReadOnlyBox(LabeledInput):
    def __init__(self, text, placeholder, *args, **kwargs):
        super().__init__(text, placeholder, *args, **kwargs)
        self.input.setReadOnly(True)
