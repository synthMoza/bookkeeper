"""
Модуль с описанием класса для отображения
и редактирования категорий
"""

from typing import Any
from PySide6 import QtWidgets, QtCore, QtGui

from bookkeeper.controllers.categories_controller import (  # type: ignore
    CategoriesController)
from bookkeeper.controllers.expenses_controller import (  # type: ignore
    ExpensesController)


class CategoriesWidget(QtWidgets.QTreeView):  # type: ignore
    """
    Виджет отображения категорий с возможностью редактирования
    и удаления категорий, отображение подкатегорий
    """

    update_category_text_signal = QtCore.Signal(str)

    def __init__(self, categories_controller: CategoriesController,
                 expenses_controller: ExpensesController,
                 *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.categories_controller = categories_controller
        self.expenses_controller = expenses_controller

        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu_callback)

        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Название категории"])
        self.model.dataChanged.connect(self.on_data_changed)
        self.setModel(self.model)
        self.selectionModel().selectionChanged.connect(self.select_callback)

        self.categories_controller.set_model(self.model)
        self.categories_controller.update_model()

    def on_data_changed(self, top_left: QtCore.QModelIndex,
                        bottom_right: QtCore.QModelIndex, roles: Any) -> None:
        """
        Коллбэк изменения названия категории
        """

        del roles

        if top_left != bottom_right:
            raise RuntimeError('unexpected selection')

        item = self.model.itemFromIndex(top_left)
        self.update_category_text_signal.emit(item.text())
        self.categories_controller.update_category_name(item.data(), item.text())

    def get_selected_category(self) -> str | None:
        """
        Получить текущую выделенную в списке категорию

        Returns
        -------
        Выделенную строку или None
        """

        selected_indexes = self.selectionModel().selectedIndexes()
        if selected_indexes:
            return_data = selected_indexes[0].data()
            if isinstance(return_data, str):
                return return_data
            return None

        return None

    def select_callback(self, selected: Any, deselected: Any) -> None:
        """
        Коллбэк выбора конкретной категории для обновления
        placeholder в соответствующем поле
        """

        del selected, deselected

        selected_category = self.get_selected_category()
        self.update_category_text_signal.emit(
            selected_category if selected_category else "")

    def open_menu_callback(self, position: QtCore.QPoint) -> None:
        """
        Коллбэк открытия меню при нажатии правой кнопки мыши
        """

        menu = QtWidgets.QMenu()

        add_category_action = QtGui.QAction("Добавить подкатегорию")
        add_category_action.triggered.connect(self.add_category_trigger)
        menu.addAction(add_category_action)

        selected_category = self.get_selected_category()
        if selected_category is not None:
            remove_category_action = QtGui.QAction("Удалить категорию")
            remove_category_action.triggered.connect(self.remove_category_trigger)
            menu.addAction(remove_category_action)

        menu.exec_(self.viewport().mapToGlobal(position))

    def add_category_trigger(self) -> None:
        """
        Триггер добавления категории, вызывающий обновление модели
        """

        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            self.expand(indexes[0])

        index = indexes[0] if indexes else None
        self.categories_controller.add_category_to_model(index)

    def remove_category_trigger(self) -> None:
        """
        Триггер удаления категории, вызывающий обновление модели
        """

        index = self.selectionModel().selectedIndexes()[0]
        self.categories_controller.delete_category_from_model(index)
        self.expenses_controller.update_model()
