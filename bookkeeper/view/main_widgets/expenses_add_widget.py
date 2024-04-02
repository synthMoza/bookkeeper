from PySide6 import QtWidgets, QtCore

from bookkeeper.view.utility_widgets.labeled_input import *
from bookkeeper.view.main_widgets.categories_widget import CategoriesWidget
from bookkeeper.controllers.expenses_controller import ExpensesController
from bookkeeper.controllers.categories_controller import CategoriesController
from bookkeeper.models.expense import Expense


class CommonButton(QtWidgets.QPushButton):
    def __init__(self, text, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.setText(self.text)
        self.clicked.connect(callback)


class ExpensesAddWidget(QtWidgets.QWidget):
    def __init__(self, expenses_controller: ExpensesController, categories_controller: CategoriesController,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.expenses_controller = expenses_controller
        self.categories_controller = categories_controller

        self.edit_pk = 0

        self.text = "Добавление расхода"
        self.label = QtWidgets.QLabel(self.text)

        self.layout.addWidget(self.label)
        categories_widget = CategoriesWidget(categories_controller, expenses_controller)

        self.fields = {
            "sum": LabeledFloatInput('Сумма', ''),
            "category": LabeledReadOnlyBox('Категория', ''),
            "category_list": categories_widget,
            "commentary": LabeledInput('Комментарий', ''),
            "date": LabeledDateInput('Дата', ''),
        }

        categories_widget.update_category_text_signal.connect(self.fields["category"].set_placeholder)

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

    def clear_inputs(self):
        self.fields["sum"].input.clear()
        self.fields["commentary"].input.clear()

    def add_expense(self, exists=False):
        amount_text = self.fields["sum"].input.text().replace(',', '.')
        if not amount_text:
            return

        indexes = self.fields["category_list"].selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            category_id = self.categories_controller.get_current_category_id(index)
        else:
            category = self.categories_controller.get_category_by_name(self.fields["category"].input.text())
            if category:
                category_id = category.pk
            else:
                return  # no category

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
            self.expenses_controller.update_expense(expense)
        else:
            self.expenses_controller.add_expense(expense)
        self.expenses_controller.update_model()
        self.clear_inputs()

    def cancel_edit(self):
        self.clear_inputs()
        self.left_button.setCurrentWidget(self.add_button)
        self.right_button.setCurrentWidget(self.reset_button)

    def apply_edit(self):
        self.add_expense(True)
        self.expenses_controller.update_model()
        self.cancel_edit()  # clear inputs and reset buttons

    def edit_expense(self, pk: int):
        self.edit_pk = pk  # save for later

        # Switch to "edit" mode
        self.left_button.setCurrentWidget(self.apply_edit_button)
        self.right_button.setCurrentWidget(self.cancel_edit_button)

        # Fill fields with the values
        expense = self.expenses_controller.get_expense(pk)
        self.fields["sum"].input.setText(str(expense.amount).replace('.', ','))
        self.fields["commentary"].input.setText(expense.comment)
        self.fields["category"].input.setText(self.categories_controller.get_category(expense.category_id).name)
