from datetime import datetime

import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category


@pytest.fixture
def expenses_repo():
    return MemoryRepository()


@pytest.fixture
def category_repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    d = datetime.now()
    e = Expense(amount=100, category_id=1, date=d, comment='test', pk=1)
    assert e.amount == 100
    assert e.category_id == 1
    assert e.comment == 'test'
    assert e.pk == 1
    assert e.date == d


def test_create_brief():
    d = datetime.now()
    e = Expense(d, 100, 1)
    assert e.amount == 100
    assert e.category_id == 1
    assert e.date == d


def test_can_add_to_repo(expenses_repo):
    d = datetime.now()
    e = Expense(d, 100, 1)
    pk = expenses_repo.add(e)
    assert e.pk == pk


def test_get_row(category_repo):
    category_id = category_repo.add(Category('test_category'))
    d = datetime(1984, 11, 25, 9, 28, 34)
    e = Expense(d, 100, category_id, 'test_comment')
    rows = e.get_rows(category_repo)
    assert rows == ["1984-11-25 09:28:34", "100", "test_category", "test_comment"]


def test_delete_expenses_of_category(expenses_repo):
    d = datetime.now()
    e1 = Expense(d, 100, 1, 'test_comment')
    e2 = Expense(d, 200, 1, 'test_comment')
    pk1 = expenses_repo.add(e1)
    pk2 = expenses_repo.add(e2)
    assert e1.pk == pk1
    assert e2.pk == pk2
    Expense.delete_expenses_of_category(expenses_repo, 1)
    assert expenses_repo.get(pk1) is None
    assert expenses_repo.get(pk2) is None

