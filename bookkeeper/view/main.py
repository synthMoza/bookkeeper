import sys

from PySide6 import QtWidgets
from bookkeeper.view.main_widgets.main_window import MainWindow

app_title = "The Bookkeeper App"


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle(app_title)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()