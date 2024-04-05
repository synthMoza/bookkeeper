"""
Главный модуль приложения, запускающий главное окно
"""

import sys

from PySide6 import QtWidgets, QtGui  # ignore: type[no-untyped-def]
from bookkeeper.view.main_widgets.main_window import MainWindow

APP_TITLE = "The Bookkeeper App"


def main() -> None:
    """
    main функция создает инстанс app, устаналивает стиль виджетов,
    устаналивает иконку и зарускает приложение
    """

    app = QtWidgets.QApplication(sys.argv)

    styles_file = "style.qss"
    with open(styles_file, "r", encoding="utf-8") as file:
        style_sheet = file.read()
        app.setStyleSheet(style_sheet)

    window = MainWindow()
    window.setWindowTitle(APP_TITLE)

    icon = QtGui.QIcon('icon.png')
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
