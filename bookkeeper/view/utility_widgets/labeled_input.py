"""
Виджеты LabeledInput - именованные поля с возможностью ввода текста
в различных модификациях
"""

from typing import Any
from datetime import datetime

from PySide6 import QtWidgets
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QDoubleValidator


class LabeledInput(QtWidgets.QWidget):  # type: ignore
    """
    Именованный виджет с вводом текста
    """
    def __init__(self, text: str, placeholder: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.input = QtWidgets.QLineEdit(placeholder)

        # without the label it will be just an input window
        if text:
            self.label = QtWidgets.QLabel(text)
            self.layout.addWidget(self.label)

        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

    #  error: Returning Any from function declared to return "str"
    def get_text(self) -> str:
        """
        Получить введенный в поле для вода текст

        Returns
        -------
        Введенный в поле текст
        """

        return self.input.text()  # type: ignore

    def set_placeholder(self, placeholder: str) -> None:
        """
        Установить новый placeholder для виджета с вводом текста

        Parameters
        ----------
        placeholder - новый текст
        """

        self.input.clear()
        self.input.insert(placeholder)


class LabeledFloatInput(LabeledInput):
    """
    Именованный виджет с вводом текста и валидацией флотов
    """
    def __init__(self, text: str, placeholder: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(text, placeholder, *args, **kwargs)
        self.input.setValidator(QDoubleValidator(self.input))


class LabeledDateInput(QtWidgets.QWidget):  # type: ignore
    """
    Именованный виджет с вводом даты
    """
    def __init__(self, text: str, *args: Any, **kwargs: Any) -> None:
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
        """
        Получить datetime из введенного в поле из qt формат в datetime формат

        Returns
        -------
        datetime в нужном формате
        """

        return datetime.strptime(self.input.dateTime().toString(self.qt_format),
                                 self.datetime_format)


class LabeledReadOnlyBox(LabeledInput):
    """
    Именованный виджет с вводом текста с флагом readonly
    """
    def __init__(self, text: str, placeholder: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(text, placeholder, *args, **kwargs)
        self.input.setReadOnly(True)
