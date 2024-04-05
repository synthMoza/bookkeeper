import datetime

import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense


@pytest.fixture
def expenses_repo():
    return MemoryRepository()


def test_create_object():
    b = Budget('День', 1000.0, 1500.0)
    assert b.interval == 'День'
    assert b.amount == 1000.0
    assert b.limit_amount == 1500.0


def test_invalid_interval(expenses_repo):
    b = Budget('Год', 0, 3000000.0)
    with pytest.raises(KeyError):
        b.update_amount(expenses_repo)


def test_update_amount(expenses_repo):
    b1 = Budget('День', 0, 1000.0)
    b2 = Budget('Неделя', 0, 7000.0)
    b3 = Budget('Месяц', 0, 30000.0)

    for i in range(10):
        e = Expense(datetime.datetime(year=2024, month=4, day=1) + datetime.timedelta(days=i), 1000.0, 1)
        expenses_repo.add(e)

    b1.update_amount(expenses_repo)
    b2.update_amount(expenses_repo)
    b3.update_amount(expenses_repo)

    assert b1.amount == 1000.0
    assert b2.amount == 7000.0
    assert b3.amount == 10000.0

