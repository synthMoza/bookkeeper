from bookkeeper.repository.sqlite_repository import SQLiteRepository
from dataclasses import dataclass
from datetime import datetime

import pytest
import sqlite3


@dataclass
class Custom():
    foo: str = 'check'
    bar: str = 'erase'
    dt: datetime = datetime(1994, 9, 25, 16, 24, 11)
    a: int = 4
    pk: int = 0


@pytest.fixture
def custom_class():
    return Custom


@pytest.fixture(autouse=True)
def repo():
    test_db_path = f'test.db'
    r = SQLiteRepository(test_db_path, Custom)
    r.create_table()
    yield r
    r.delete_all()
    r.drop_table()


def test_crud(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    obj2.a = 6
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_delete_nonexistent(repo):
    with pytest.raises(KeyError):
        repo.delete(1)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)
    with pytest.raises(ValueError):
        repo.update(0)


def test_get_all(repo, custom_class):
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.a = i
        o.bar = 'test'
        repo.add(o)
        objects.append(o)
    assert repo.get_all({'a': 0}) == [objects[0]]
    assert repo.get_all({'bar': 'test'}) == objects
    assert repo.get_all({'a': -1}) == []


def test_delete_all(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.a = i
        o.bar = 'test'
        repo.add(o)
        objects.append(o)
    repo.delete_all()
    assert repo.get_all() == []


def test_none_field(repo, custom_class):
    obj = custom_class()
    obj.foo = None
    pk = repo.add(obj)
    assert repo.get(pk).foo == obj.foo


# Тесты FOREIGN_KEY

@dataclass
class Custom0():
    foo: str = ''
    bar: int = 0
    pk: int = 0


@pytest.fixture
def foreign_custom_class0():
    return Custom0


@dataclass
class Custom1():
    fk: int = 0
    pk: int = 0


@pytest.fixture
def foreign_custom_class1():
    return Custom1


@pytest.fixture(autouse=True)
def foreign_repo0():
    test_db_path = f'test0.db'
    with sqlite3.connect(test_db_path) as con:
        cur = con.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {Custom0.__name__.lower()} "
            f"(pk INTEGER PRIMARY KEY, foo TEXT, bar INTEGER)"
        )

    r = SQLiteRepository(test_db_path, Custom0)
    yield r
    r.delete_all()
    r.drop_table()


@pytest.fixture(autouse=True)
def foreign_repo1():
    test_db_path = f'test0.db'
    with sqlite3.connect(test_db_path) as con:
        cur = con.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {Custom1.__name__.lower()} "
            f"(pk INTEGER PRIMARY KEY, fk INTEGER, FOREIGN KEY (fk) REFERENCES {Custom0.__name__.lower()}(pk))"
        )

    r = SQLiteRepository(test_db_path, Custom1)
    yield r
    r.delete_all()
    r.drop_table()


def test_foreign_keys(foreign_repo0, foreign_repo1, foreign_custom_class0, foreign_custom_class1):
    obj0 = foreign_custom_class0()
    obj1 = foreign_custom_class1()

    obj0.bar = 4
    obj0.foo = 'four'

    foreign_repo0.add(obj0)

    obj1.fk = 2 * obj0.pk + 3
    with pytest.raises(sqlite3.IntegrityError):
        foreign_repo1.add(obj1)

    obj1.fk = obj0.pk
    foreign_repo1.add(obj1)
