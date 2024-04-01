from PySide6 import QtGui, QtCore

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.category import Category


class CategoriesController(QtCore.QObject):
    """
        Класс реализует паттерн Controller из архитектуры MVC для модели Expense
    """

    # Signal ExpensesController to delete expense
    delete_expense_signal = QtCore.Signal(int)

    def __init__(self, categories_repo: AbstractRepository[Category]) -> None:
        super().__init__()
        self.repo = categories_repo
        self.model = None

    def set_model(self, model: QtGui.QStandardItemModel) -> None:
        """
        Установить соответствующую модель. Необходимо вынести в отдельную функцию, т.к. модели еще нет
        при инициализации контроллера
        """

        if not self.model:
            self.model = model

    def get_category(self, pk: int) -> Category | None:
        """
        Получить категорию по ключу

        Parameters
        ----------
        pk - ключ категории

        Returns
        -------
        Category или None, если расхода с таким ключом нет
        """

        return self.repo.get(pk)

    def update_model(self):
        """
        Обновить внутреннюю модель значениями категорий из репозитория.
        """

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

    def add_category(self, c: Category):
        """
        Добавить новую категорию в репозиторий. Если она уже существует,
        то она не обновится.

        Parameters
        ----------
        e - новая категория
        """

        self.repo.add(c)

    def update_category_name(self, pk: int, name: str) -> None:
        """
        Обновить название категории по ключу в репозитории

        Parameters
        ----------
        pk - ключ затраты из репозитория
        name - новое название категории
        """

        new_category = self.repo.get(pk)
        new_category.name = name
        self.repo.update(new_category)

    def get_current_category_id(self, idx: QtCore.QModelIndex) -> int | None:
        """
        Получить текущую выделенную в интерфейсе категорию по индексу

        Parameters
        ----------
        idx - индекс категории в модели
        """

        if idx:
            return self.model.itemFromIndex(idx).data()
        else:
            return None

    def add_category_to_model(self, idx: QtCore.QModelIndex | None):
        """
        Добавить новую категорию как подкатегорию категории с индексом idx

        Parameters
        ----------
        idx - индекс родительской категории или None
        """

        standard_name = 'Новая категория'
        item = QtGui.QStandardItem(standard_name)

        if idx:
            parent_category = self.model.itemFromIndex(idx)
            parent_category.appendRow(item)
            category = Category(standard_name, parent_category.data())
        else:
            self.model.appendRow(item)
            category = Category(standard_name, None)

        self.add_category(category)
        item.setData(category.pk)

    def delete_category_from_model(self, idx: QtCore.QModelIndex | None):
        """
        Полностью удалить категорию из модели. Использует сигнал к ExpensesController для удаления всех затрат
        данной категории и всех подкатегорий

        Parameters
        ----------
        idx - индекс категории
        """

        item = self.model.itemFromIndex(idx)

        category = self.repo.get(item.data())
        all_categories = list(category.get_subcategories(self.repo)) + [category]
        for subcategory in all_categories:
            self.delete_expense_signal.emit(subcategory.pk)
            self.repo.delete(subcategory.pk)

        self.model.removeRow(idx.row(), idx.parent())

    def get_category_by_name(self, name: str) -> Category | None:
        """
        Получить категорию из репозитория по имени

        Parameters
        ----------
        name - название категории

        Returns
        -------
        Найденную Category или None
        """

        categories = self.repo.get_all({"name": name})
        if categories:
            return categories[0]
        else:
            return None
