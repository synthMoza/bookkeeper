import sys

from PySide6 import QtWidgets, QtGui
from bookkeeper.view.main_widgets.main_window import MainWindow

app_title = "The Bookkeeper App"


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    window = MainWindow()
    window.setWindowTitle(app_title)

    icon = QtGui.QIcon('icon.png')
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
