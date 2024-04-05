"""
Модуль с описанием реализации репозитория на основе sqlite
"""

from inspect import get_annotations
from typing import Any, Dict, Type, get_args
from datetime import datetime

import sqlite3

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
        Репозиторий, работающий с SQLite. Хранит данные в DB файле, взаимодействуя
        через SQL запросы
    """

    def __init__(self, db_file: str, cls: Type[T]) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.generic_type: Type[T] = cls

    @staticmethod
    def set_pragmas(cur: sqlite3.Cursor) -> None:
        """
        Установить в курсор необходимые pragma
        """

        cur.execute('PRAGMA foreign_keys = ON')

    _types: Dict[type, str] = {
        int: 'INTEGER',
        str: 'TEXT',
        float: 'REAL',
        datetime: 'DATETIME'
    }

    def create_table(self) -> None:
        """
        Создать дефолтную таблицу в базе данных
        """

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            fields = ', '.join([f'{k} {self._types[v]}' for k, v in self.fields.items()])
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table_name} "
                f"(pk INTEGER PRIMARY KEY, {fields})"
            )

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) is None:
            raise ValueError(f'trying to add object {obj} without `pk` attribute')
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')

        names = ', '.join(self.fields.keys())
        parameters = ', '.join("?" * len(self.fields))

        values = [self._attr_to_sql(getattr(obj, x)) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            query = f'INSERT INTO {self.table_name}({names}) VALUES({parameters})'
            cur.execute(query, values)
            if cur.lastrowid is not None:
                obj.pk = cur.lastrowid
            else:
                raise RuntimeError('failed to insert')
        con.close()
        return obj.pk

    def get(self, primary_key: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            cur.execute(f'SELECT * FROM {self.table_name} WHERE pk={primary_key}')
            raw_obj = cur.fetchone()
            if raw_obj is None:
                return None

        return self._to_obj(raw_obj, cur.description)

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            if where:
                conditions = ", ".join([f"{k}=?" for k in where.keys()])
                query = f'SELECT * FROM {self.table_name} WHERE {conditions}'
                cur.execute(query, [self._attr_to_sql(v) for v in where.values()])
            else:
                query = f'SELECT * FROM {self.table_name}'
                cur.execute(query)
            raw_objs = cur.fetchall()
            if not raw_objs:
                return []

        return [self._to_obj(raw_obj, cur.description) for raw_obj in raw_objs]

    datetime_format = '%Y-%m-%d %H:%M:%S'

    def _attr_to_sql(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, datetime):
            return f'{datetime.strftime(value, self.datetime_format)}'
        if value is None:
            return 'NULL'
        return str(value)

    def _sql_to_attr(self, field: Type[Any], value: Any) -> Any:
        if value == 'NULL':
            return None
        if str == field or str in get_args(field):
            value = value.strip('\'')
            return str(value)
        if datetime == field or datetime in get_args(field):
            value = value.strip('\'')
            return datetime.strptime(value, self.datetime_format)
        return value

    def _to_obj(self, raw_obj: Any, desc: Any) -> T:
        obj = self.generic_type.__new__(self.generic_type)
        setattr(obj, 'pk', raw_obj[0])
        for i, field in enumerate(desc):
            if field[0] in self.fields:
                field_val = self.fields[field[0]]
                setattr(obj, field[0], self._sql_to_attr(field_val, raw_obj[i]))
            else:
                setattr(obj, field[0], raw_obj[i])

        return obj

    def update(self, obj: T) -> None:
        if getattr(obj, 'pk', None) is None:
            raise ValueError(f'trying to update object {obj} '
                             f'without `pk` attribute')
        if self.get(obj.pk) is None:
            raise ValueError(f'trying to update object {obj} '
                             f'that is not in the repository')

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            fields = ', '.join([f'{v}=?' for v in self.fields.keys()])
            query = f"UPDATE {self.table_name} SET {fields} WHERE pk={obj.pk}"
            values = [self._attr_to_sql(getattr(obj, v)) for v in self.fields.keys()]
            cur.execute(query, values)

    def delete(self, primary_key: int) -> None:
        if self.get(primary_key) is None:
            raise KeyError(f"failed to find object with "
                           f"pk={primary_key} in the repository")

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            query = f"DELETE FROM {self.table_name} WHERE pk= {primary_key}"
            cur.execute(query)

    def delete_all(self) -> None:
        """
        Удалить все записи из базы данных
        """

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            query = f"DELETE FROM {self.table_name}"
            cur.execute(query)

    def drop_table(self) -> None:
        """
        Удалить таблицу из нижележащей базы данных
        """

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            query = f"DROP TABLE {self.table_name}"
            cur.execute(query)
