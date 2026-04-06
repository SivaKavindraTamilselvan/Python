"""
lightweight_orm.py
──────────────────
A from-scratch ORM built on Python metaclasses, descriptors, and sqlite3.

Covers:
  • Field descriptors   (__get__ / __set__ / __set_name__)
  • ModelMeta           (__new__ + __init_subclass__)
  • DDL auto-generation (CREATE TABLE)
  • CRUD               (.save(), .delete())
  • QuerySet            (.filter(), .order_by(), .all(), .first(), .count())
  • ForeignKey          (lazy-loaded via descriptor __get__)
"""

import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple, Type

# 1. DATABASE CONNECTION

_local = threading.local()
_db_path: str = ":memory:"

def connect(path: str = ":memory:") -> None:
    global _db_path
    _db_path = path


#to prevent from opening the connection repeatedly
def _get_conn() -> sqlite3.Connection:
    if not getattr(_local, "conn", None):
        _local.conn = sqlite3.connect(_db_path)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA foreign_keys = ON")
    return _local.conn


def _execute(sql: str, params: tuple = ()) -> sqlite3.Cursor:
    conn = _get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur


# 2. FIELD DESCRIPTORS

class Field:

    _sql_type: str = "TEXT"

    def __init__(
        self,
        *,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        unique: bool = False,
    ):
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.name: str = ""


    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, self.default)

    def __set__(self, obj, value) -> None:
        value = self.validate(value)
        obj.__dict__[self.name] = value


    def validate(self, value: Any) -> Any:
        if value is None:
            if not self.nullable and not self.primary_key:
                raise ValueError(f"Field '{self.name}' cannot be None")
            return value
        return value


    def column_def(self) -> str:
        parts = [self.name, self._sql_type]
        if self.primary_key:
            parts.append("PRIMARY KEY AUTOINCREMENT")
        if not self.nullable and not self.primary_key:
            parts.append("NOT NULL")
        if self.unique:
            parts.append("UNIQUE")
        if self.default is not None:
            parts.append(f"DEFAULT {self._format_default(self.default)}")
        return " ".join(parts)

    def _format_default(self, v: Any) -> str:
        return f"'{v}'" if isinstance(v, str) else str(v)


class IntegerField(Field):
    _sql_type = "INTEGER"

    def validate(self, value):
        value = super().validate(value)
        if value is not None and not isinstance(value, int):
            raise TypeError(f"Field '{self.name}' expects int, got {type(value).__name__}")
        return value


class FloatField(Field):
    _sql_type = "REAL"

    def validate(self, value):
        value = super().validate(value)
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError(f"Field '{self.name}' expects float, got {type(value).__name__}")
        return float(value) if value is not None else None


class TextField(Field):
    _sql_type = "TEXT"

    def validate(self, value):
        value = super().validate(value)
        if value is not None:
            return str(value)
        return value


class BooleanField(Field):
    _sql_type = "INTEGER"

    def validate(self, value):
        value = super().validate(value)
        if value is not None and not isinstance(value, bool):
            raise TypeError(f"Field '{self.name}' expects bool")
        return int(value) if value is not None else None

    def __get__(self, obj, objtype=None):
        raw = super().__get__(obj, objtype)
        if obj is None:
            return self
        return bool(raw) if raw is not None else None


# 3. FOREIGNKEY DESCRIPTOR

class ForeignKey(Field):
    _sql_type = "INTEGER"
    def __init__(self, to_model, *, nullable: bool = True, on_delete: str = "CASCADE"):
        super().__init__(nullable=nullable)
        self.to_model = to_model        # the related Model class (or a string name)
        self.on_delete = on_delete

    def __set_name__(self, owner, name):
        self.name = name
        self.id_attr = f"{name}_id"     # the actual column stored in the DB row

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Lazy load: check cache first
        cache_key = f"_cache_{self.name}"
        cached = obj.__dict__.get(cache_key)
        if cached is not None:
            return cached
        fk_value = obj.__dict__.get(self.id_attr)
        if fk_value is None:
            return None
        related_model = self._resolve_model()
        related_obj = related_model.get(id=fk_value)
        obj.__dict__[cache_key] = related_obj   # cache so we don't re-query
        return related_obj

    def __set__(self, obj, value):
        if value is None:
            obj.__dict__[self.id_attr] = None
            obj.__dict__.pop(f"_cache_{self.name}", None)
        elif isinstance(value, int):
            obj.__dict__[self.id_attr] = value
            obj.__dict__.pop(f"_cache_{self.name}", None)
        else:
            obj.__dict__[self.id_attr] = value.id
            obj.__dict__[f"_cache_{self.name}"] = value

    def _resolve_model(self):
        if isinstance(self.to_model, str):
            return ModelMeta._registry[self.to_model]
        return self.to_model

    def column_def(self) -> str:
        related = self._resolve_model()
        return (
            f"{self.id_attr} INTEGER REFERENCES "
            f"{related._meta['table_name']}(id) ON DELETE {self.on_delete}"
        )


# 4. QUERYSET  (method-chaining query builder)

_LOOKUP_OPS = {
    "eq":       "=",
    "ne":       "!=",
    "lt":       "<",
    "lte":      "<=",
    "gt":       ">",
    "gte":      ">=",
    "like":     "LIKE",
    "in":       "IN",
    "isnull":   "IS NULL",
}


class QuerySet:

    def __init__(self, model_class):
        self._model = model_class
        self._filters: List[Tuple[str, str, Any]] = []  # (col, op, value)
        self._order: List[str] = []
        self._limit: Optional[int] = None
        self._offset: int = 0


    def _clone(self) -> "QuerySet":
        qs = QuerySet(self._model)
        qs._filters = self._filters[:]
        qs._order = self._order[:]
        qs._limit = self._limit
        qs._offset = self._offset
        return qs


    def filter(self, **kwargs) -> "QuerySet":
        qs = self._clone()
        for key, value in kwargs.items():
            parts = key.rsplit("__", 1)
            if len(parts) == 2 and parts[1] in _LOOKUP_OPS:
                col, op = parts[0], parts[1]
            else:
                col, op = key, "eq"
            qs._filters.append((col, op, value))
        return qs


    def order_by(self, *fields) -> "QuerySet":

        qs = self._clone()
        for f in fields:
            if f.startswith("-"):
                qs._order.append(f"{f[1:]} DESC")
            else:
                qs._order.append(f"{f} ASC")
        return qs

    def limit(self, n: int) -> "QuerySet":
        qs = self._clone()
        qs._limit = n
        return qs

    def offset(self, n: int) -> "QuerySet":
        qs = self._clone()
        qs._offset = n
        return qs


    def _build_sql(self) -> Tuple[str, tuple]:
        table = self._model._meta["table_name"]
        where_clauses, params = [], []

        for col, op, value in self._filters:
            sql_op = _LOOKUP_OPS[op]
            if op == "isnull":
                where_clauses.append(f"{col} {'IS NULL' if value else 'IS NOT NULL'}")
            elif op == "in":
                placeholders = ", ".join("?" * len(value))
                where_clauses.append(f"{col} IN ({placeholders})")
                params.extend(value)
            else:
                where_clauses.append(f"{col} {sql_op} ?")
                params.append(value)

        sql = f"SELECT * FROM {table}"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        if self._order:
            sql += " ORDER BY " + ", ".join(self._order)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        if self._offset:
            sql += f" OFFSET {self._offset}"

        return sql, tuple(params)

    def all(self) -> List:
        sql, params = self._build_sql()
        rows = _execute(sql, params).fetchall()
        return [self._model._from_row(row) for row in rows]

    def first(self) -> Optional[object]:
        results = self.limit(1).all()
        return results[0] if results else None

    def count(self) -> int:
        table = self._model._meta["table_name"]
        where_clauses, params = [], []
        for col, op, value in self._filters:
            sql_op = _LOOKUP_OPS[op]
            if op == "isnull":
                where_clauses.append(f"{col} {'IS NULL' if value else 'IS NOT NULL'}")
            elif op == "in":
                placeholders = ", ".join("?" * len(value))
                where_clauses.append(f"{col} IN ({placeholders})")
                params.extend(value)
            else:
                where_clauses.append(f"{col} {sql_op} ?")
                params.append(value)
        sql = f"SELECT COUNT(*) FROM {table}"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        return _execute(sql, tuple(params)).fetchone()[0]

    def delete(self) -> int:
        table = self._model._meta["table_name"]
        where_clauses, params = [], []
        for col, op, value in self._filters:
            sql_op = _LOOKUP_OPS[op]
            if op == "in":
                placeholders = ", ".join("?" * len(value))
                where_clauses.append(f"{col} IN ({placeholders})")
                params.extend(value)
            else:
                where_clauses.append(f"{col} {sql_op} ?")
                params.append(value)
        sql = f"DELETE FROM {table}"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        cur = _execute(sql, tuple(params))
        return cur.rowcount


    def __iter__(self):
        return iter(self.all())

    def __repr__(self):
        return f"<QuerySet [{self._model.__name__}] filters={self._filters}>"


# 5. MODELMETA  (the metaclass)

class ModelMeta(type):

    _registry: Dict[str, type] = {}   # class-name → class (for FK forward refs)

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        fields: Dict[str, Field] = {}

        # Inherit fields from parent models
        for base in bases:
            if hasattr(base, "_meta"):
                fields.update(base._meta.get("fields", {}))

        for attr, val in namespace.items():
            if isinstance(val, Field):
                fields[attr] = val

        if "id" not in fields and name != "Model":
            id_field = IntegerField(primary_key=True, nullable=True)
            id_field.name = "id"
            namespace["id"] = id_field
            fields["id"] = id_field

        namespace["_meta"] = {
            "table_name": name.lower() + "s",  # e.g. User → users
            "fields": fields,
        }

        cls = super().__new__(mcs, name, bases, namespace)
        mcs._registry[name] = cls
        return cls


# 6. MODEL BASE CLASS

class Model(metaclass=ModelMeta):

    def __init_subclass__(cls, table: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if table:
            cls._meta["table_name"] = table


    def __init__(self, **kwargs):
        for field_name, field in self._meta["fields"].items():
            if isinstance(field, ForeignKey):
                if field_name in kwargs:
                    setattr(self, field_name, kwargs[field_name])
                elif field.id_attr in kwargs:
                    self.__dict__[field.id_attr] = kwargs[field.id_attr]
                else:
                    self.__dict__[field.id_attr] = None
            else:
                value = kwargs.get(field_name, field.default)
                setattr(self, field_name, value)


    @classmethod
    def create_table(cls, if_not_exists: bool = True) -> None:
        cols = []
        for field in cls._meta["fields"].values():
            cols.append(field.column_def())
        exists = "IF NOT EXISTS " if if_not_exists else ""
        sql = (
            f"CREATE TABLE {exists}{cls._meta['table_name']} "
            f"({', '.join(cols)})"
        )
        _execute(sql)

    @classmethod
    def drop_table(cls) -> None:
        _execute(f"DROP TABLE IF EXISTS {cls._meta['table_name']}")


    def save(self) -> "Model":
        fields = self._meta["fields"]
        if self.id is None:
            # INSERT
            cols, placeholders, vals = [], [], []
            for name, field in fields.items():
                if field.primary_key:
                    continue
                if isinstance(field, ForeignKey):
                    cols.append(field.id_attr)
                    vals.append(self.__dict__.get(field.id_attr))
                else:
                    cols.append(name)
                    vals.append(self.__dict__.get(name, field.default))
            sql = (
                f"INSERT INTO {self._meta['table_name']} "
                f"({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"
            )
            cur = _execute(sql, tuple(vals))
            self.__dict__["id"] = cur.lastrowid
        else:
            # UPDATE
            set_parts, vals = [], []
            for name, field in fields.items():
                if field.primary_key:
                    continue
                if isinstance(field, ForeignKey):
                    set_parts.append(f"{field.id_attr} = ?")
                    vals.append(self.__dict__.get(field.id_attr))
                else:
                    set_parts.append(f"{name} = ?")
                    vals.append(self.__dict__.get(name, field.default))
            vals.append(self.id)
            sql = (
                f"UPDATE {self._meta['table_name']} "
                f"SET {', '.join(set_parts)} WHERE id = ?"
            )
            _execute(sql, tuple(vals))
        return self

    def delete(self) -> None:
        if self.id is None:
            raise ValueError("Cannot delete an unsaved instance")
        _execute(
            f"DELETE FROM {self._meta['table_name']} WHERE id = ?",
            (self.id,),
        )
        self.__dict__["id"] = None


    @classmethod
    def filter(cls, **kwargs) -> QuerySet:
        return QuerySet(cls).filter(**kwargs)

    @classmethod
    def all(cls) -> List:
        return QuerySet(cls).all()

    @classmethod
    def get(cls, **kwargs) -> Optional["Model"]:
        return QuerySet(cls).filter(**kwargs).first()

    @classmethod
    def count(cls) -> int:
        return QuerySet(cls).count()


    @classmethod
    def _from_row(cls, row: sqlite3.Row) -> "Model":
        """Build a model instance from a sqlite3.Row without validation overhead."""
        obj = cls.__new__(cls)
        obj.__dict__.update(dict(row))
        return obj


    def __repr__(self):
        fields = self._meta["fields"]
        attrs = []
        for name, field in fields.items():
            if isinstance(field, ForeignKey):
                attrs.append(f"{field.id_attr}={self.__dict__.get(field.id_attr)!r}")
            else:
                attrs.append(f"{name}={self.__dict__.get(name)!r}")
        return f"<{self.__class__.__name__} {' '.join(attrs)}>"


# 7. DEMONSTRATION

if __name__ == "__main__":

    connect("myapp.db")

    class User(Model):
        name   = TextField(nullable=False)
        email  = TextField(unique=True, nullable=False)
        age    = IntegerField(nullable=False)
        active = BooleanField(default=True)

    class Post(Model):
        title   = TextField(nullable=False)
        body    = TextField()
        author  = ForeignKey(User)
        views   = IntegerField(default=0)

    User.create_table()
    Post.create_table()

    print("=== CREATE TABLE SQL for User ===")
    cols = [f.column_def() for f in User._meta["fields"].values()]
    print(f"CREATE TABLE users ({', '.join(cols)})\n")


    alice = User(name="Alice", email="alice@example.com", age=30).save()
    bob   = User(name="Bob",   email="bob@example.com",   age=22).save()
    carol = User(name="Carol", email="carol@example.com", age=27).save()

    print("=== Saved users ===")
    for u in User.all():
        print(u)


    p1 = Post(title="Hello World", body="First post!", author=alice, views=10).save()
    p2 = Post(title="ORM Deep Dive", body="Metaclasses rock.", author=alice, views=42).save()
    p3 = Post(title="Bob's Blog", body="Hi there.", author=bob, views=5).save()

    print("\n=== Post with lazy-loaded author ===")
    loaded_post = Post.get(id=p2.id)
    print(f"Post: '{loaded_post.title}' → author: {loaded_post.author.name}")

    print("\n=== Users age >= 25, sorted by name DESC ===")
    results = User.filter(age__gte=25).order_by("-name").all()
    for u in results:
        print(f"  {u.name}, age {u.age}")

    print("\n=== Posts with views > 5, sorted by views DESC ===")
    for p in Post.filter(views__gt=5).order_by("-views").all():
        print(f"  [{p.views} views] {p.title}")

    print(f"\nTotal users: {User.count()}")
    print(f"Users age < 25: {User.filter(age__lt=25).count()}")

    bob.age = 23
    bob.save()
    print(f"\nBob's updated age: {User.get(id=bob.id).age}")

    carol.delete()
    print(f"Users after deleting Carol: {User.count()}")

    print("\n All ORM features demonstrated successfully.")