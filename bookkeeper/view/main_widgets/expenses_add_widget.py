import PySide6.QtCore
from PySide6 import QtWidgets, QtCore

from bookkeeper.view.utility_widgets.labeled_input import *
from bookkeeper.view.main_widgets.categories_widget import CategoriesWidget
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category


class CommonButton(QtWidgets.QPushButton):
    def __init__(self, text, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.setText(self.text)
        self.clicked.connect(callback)


class ExpensesAddWidget(QtWidgets.QWidget):
    update_expenses_signal = QtCore.Signal()

    def __init__(self, categories_repo: AbstractRepository[Category],
                 expenses_repo: AbstractRepository[Expense], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.categories_repo = categories_repo
        self.expenses_repo = expenses_repo

        self.edit_pk = 0

        self.text = "Добавление расхода"
        self.label = QtWidgets.QLabel(self.text)

        self.layout.addWidget(self.label)
        categories_widget = CategoriesWidget(categories_repo)

        self.fields = {
            "sum": LabeledFloatInput('Сумма', ''),
            "category": LabeledReadOnlyBox('Категория', ''),
            "category_list": categories_widget,
            "commentary": LabeledInput('Комментарий', ''),
            "date": LabeledDateInput('Дата', ''),
        }

        categories_widget.update_category_text_signal.connect(self.fields["category"].set_placeholder)
        categories_widget.delete_expenses_of_category_signal.connect(self.delete_expenses_of_category)
        categories_widget.update_expenses_signal.connect(self.update_expenses)

        for label, labeled_input in self.fields.items():
            self.layout.addWidget(labeled_input)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.add_button = CommonButton("Добавить", self.add_expense)
        self.reset_button = CommonButton("Очистить", self.clear_inputs)
        self.apply_edit_button = CommonButton("Применить", self.apply_edit)
        self.cancel_edit_button = CommonButton("Отменить", self.cancel_edit)

        self.left_button = QtWidgets.QStackedWidget()
        self.right_button = QtWidgets.QStackedWidget()

        self.left_button.addWidget(self.add_button)
        self.left_button.addWidget(self.apply_edit_button)
        self.right_button.addWidget(self.reset_button)
        self.right_button.addWidget(self.cancel_edit_button)

        self.left_button.setCurrentIndex(0)
        self.left_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)
        self.right_button.setCurrentIndex(0)
        self.right_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)

        self.button_layout.addWidget(self.left_button, stretch=1)
        self.button_layout.addWidget(self.right_button, stretch=1)
        self.layout.addLayout(self.button_layout, stretch=1)

        self.setLayout(self.layout)

    @QtCore.Slot(int)
    def delete_expenses_of_category(self, category_id: int):
        expenses = self.expenses_repo.get_all({"category_id": category_id})
        for expense in expenses:
            self.expenses_repo.delete(expense.pk)
        self.categories_repo.get_all()

    def update_expenses(self):
        self.update_expenses_signal.emit()

    def clear_inputs(self):
        self.fields["sum"].input.clear()
        self.fields["commentary"].input.clear()

    def add_expense(self, exists=False):
        amount_text = self.fields["sum"].input.text().replace(',', '.')
        if not amount_text:
            return

        category_id = self.fields["category_list"].get_current_category_id()
        if category_id is None:
            category_id = self.categories_repo.get_all({"name": self.fields["category"].input.text()})[0].pk

        date = self.fields["date"].get_datetime()
        comment = self.fields["commentary"].input.text()

        expense = Expense(
            amount=float(amount_text),
            category_id=category_id,
            date=date,
            comment=comment,
        )

        if exists:
            expense.pk = self.edit_pk
            self.expenses_repo.update(expense)
        else:
            self.expenses_repo.add(expense)
        self.update_expenses_signal.emit()
        self.clear_inputs()

    def cancel_edit(self):
        self.clear_inputs()
        self.left_button.setCurrentWidget(self.add_button)
        self.right_button.setCurrentWidget(self.reset_button)

    def apply_edit(self):
        self.add_expense(True)
        self.update_expenses()
        self.cancel_edit()  # clear inputs and reset buttons

    def edit_expense(self, pk: int):
        self.edit_pk = pk  # save for later

        # Switch to "edit" mode
        self.left_button.setCurrentWidget(self.apply_edit_button)
        self.right_button.setCurrentWidget(self.cancel_edit_button)

        # Fill fields with the values
        expense = self.expenses_repo.get(pk)
        self.fields["sum"].input.setText(str(expense.amount).replace('.', ','))
        self.fields["commentary"].input.setText(expense.comment)
        self.fields["category"].input.setText(self.categories_repo.get(expense.category_id).name)
