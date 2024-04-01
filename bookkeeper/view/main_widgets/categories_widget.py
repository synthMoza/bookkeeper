from PySide6 import QtWidgets, QtCore, QtGui

from bookkeeper.view.utility_widgets.scrollable_text_widget import ScrollableTextWidget
from bookkeeper.view.utility_widgets.labeled_input import LabeledInput
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.category import Category


class CategoriesWidget(QtWidgets.QTreeView):
    update_category_text_signal = QtCore.Signal(str)
    delete_expenses_of_category_signal = QtCore.Signal(int)
    update_expenses_signal = QtCore.Signal()

    def __init__(self, repo: AbstractRepository[Category], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.repo = repo

        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu_callback)

        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Название категории"])
        self.model.dataChanged.connect(self.on_data_changed)
        self.setModel(self.model)
        self.selectionModel().selectionChanged.connect(self.select_callback)

        self.update_categories()

    def update_categories(self):
        all_categories = self.repo.get_all()

        categories_dict = dict()
        for category in all_categories:
            item = QtGui.QStandardItem(category.name)
            item.setData(category.pk)

            categories_dict[category.pk] = item
            if category.parent is None:
                self.model.appendRow(item)
            else:
                parent_item = categories_dict[category.parent]
                parent_item.appendRow(item)

    def on_data_changed(self, top_left, bottom_right, roles):
        if top_left == bottom_right:
            item = self.model.itemFromIndex(top_left)
            self.update_category_text_signal.emit(item.text())

            new_category = self.repo.get(item.data())
            new_category.name = item.text()
            self.repo.update(new_category)

    def get_selected_category(self) -> str | None:
        selected_indexes = self.selectionModel().selectedIndexes()
        if selected_indexes:
            return selected_indexes[0].data()
        else:
            return None

    def get_current_category_id(self) -> int | None:
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            idx = indexes[0]
            return self.model.itemFromIndex(idx).data()
        else:
            return None

    def select_callback(self, selected, deselected):
        selected_category = self.get_selected_category()
        self.update_category_text_signal.emit(selected_category if selected_category else "")

    def open_menu_callback(self, position):
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

    def add_category_trigger(self):
        selected_indexes = self.selectionModel().selectedIndexes()
        standard_name = 'Новая категория'
        item = QtGui.QStandardItem(standard_name)

        if selected_indexes:
            index = selected_indexes[0]
            self.expand(index)
            parent_category = self.model.itemFromIndex(index)
            parent_category.appendRow(item)
            category = Category(standard_name, parent_category.data())
        else:
            self.model.appendRow(item)
            category = Category(standard_name, None)

        self.repo.add(category)
        item.setData(category.pk)

    def remove_category_trigger(self):
        index = self.selectionModel().selectedIndexes()[0]
        item = self.model.itemFromIndex(index)
        category = self.repo.get(item.data())
        all_categories = list(category.get_subcategories(self.repo)) + [category]
        for subcategory in all_categories:
            self.delete_expenses_of_category_signal.emit(subcategory.pk)
            self.repo.delete(subcategory.pk)
            self.update_expenses_signal.emit()

        self.model.removeRow(index.row(), index.parent())

