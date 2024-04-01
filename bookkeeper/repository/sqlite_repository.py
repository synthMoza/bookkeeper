from inspect import get_annotations

from bookkeeper.repository.abstract_repository import AbstractRepository, T
from datetime import datetime
from typing import Any, Dict, Union, get_origin, get_args

import sqlite3


class SQLiteRepository(AbstractRepository[T]):
    """
        Репозиторий, работающий с SQLite. Хранит данные в DB файле, взаимодействуя
        через SQL запросы
    """

    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.generic_type = cls

    @staticmethod
    def set_pragmas(cur):
        cur.execute('PRAGMA foreign_keys = ON')

    _types: Dict[type, str] = {
        int: 'INTEGER',
        str: 'TEXT',
        float: 'REAL',
        datetime: 'DATETIME'
    }

    def create_table(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table_name} "
                f"(pk INTEGER PRIMARY KEY, {', '.join([f'{k} {self._types[v]}' for k, v in self.fields.items()])})"
            )

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) is None:
            raise ValueError(f'trying to add object {obj} without `pk` attribute')
        elif getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')

        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))

        values = [self._attr_to_sql(getattr(obj, x)) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            q = f'INSERT INTO {self.table_name}({names}) VALUES({p})'
            cur.execute(q, values)
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            cur.execute(f'SELECT * FROM {self.table_name} WHERE pk={pk}')
            raw_obj = cur.fetchone()
            if raw_obj is None:
                return None

        return self._to_obj(raw_obj, cur.description)

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            if where:
                q = f'SELECT * FROM {self.table_name} WHERE {", ".join([f"{k}=?" for k in where.keys()])}'
                cur.execute(q, [self._attr_to_sql(v) for v in where.values()])
            else:
                q = f'SELECT * FROM {self.table_name}'
                cur.execute(q)
            raw_objs = cur.fetchall()
            if not raw_objs:
                return []

        return [self._to_obj(raw_obj, cur.description) for raw_obj in raw_objs]

    datetime_format = '%Y-%m-%d %H:%M:%S'

    def _attr_to_sql(self, v):
        if isinstance(v, str):
            return v
        elif isinstance(v, datetime):
            return f'{datetime.strftime(v, self.datetime_format)}'
        elif v is None:
            return 'NULL'
        else:
            return str(v)

    def _sql_to_attr(self, f, v):
        if v == 'NULL':
            return None
        elif str == f or str in get_args(f):
            v = v.strip('\'')
            return str(v)
        elif datetime == f or datetime in get_args(f):
            v = v.strip('\'')
            return datetime.strptime(v, self.datetime_format)
        else:
            return v

    def _to_obj(self, raw_obj, desc):
        obj = self.generic_type.__new__(self.generic_type)
        setattr(obj, 'pk', raw_obj[0])
        for i, f in enumerate(desc):
            if f[0] in self.fields:
                t = self.fields[f[0]]
                setattr(obj, f[0], self._sql_to_attr(t, raw_obj[i]))
            else:
                setattr(obj, f[0], raw_obj[i])

        return obj

    def update(self, obj: T) -> None:
        if getattr(obj, 'pk', None) is None:
            raise ValueError(f'trying to update object {obj} without `pk` attribute')
        if self.get(obj.pk) is None:
            raise ValueError(f'trying to update object {obj} that is not in the repository')

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            q = f"UPDATE {self.table_name} SET {', '.join([f'{v}=?' for v in self.fields.keys()])} WHERE pk={obj.pk}"
            cur.execute(q, [self._attr_to_sql(getattr(obj, v)) for v in self.fields.keys()])

    def delete(self, pk: int) -> None:
        if self.get(pk) is None:
            raise KeyError(f"failed to find object with pk={pk} in the repository")

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            q = f"DELETE FROM {self.table_name} WHERE pk= {pk}"
            cur.execute(q)

    def delete_all(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            q = f"DELETE FROM {self.table_name}"
            cur.execute(q)

    def drop_table(self):
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            self.set_pragmas(cur)
            q = f"DROP TABLE {self.table_name}"
            cur.execute(q)
