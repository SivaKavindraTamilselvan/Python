import sqlite3
from ORM.Practice.fields import Field

def log_query(method):
    def wrapper(cls, sql, params=()):
        print(f"[SQL] {sql}  | params={params}")
        return method(cls, sql, params)
    wrapper.__name__ = method.__name__
    return wrapper


class Model:

    connection = sqlite3.connect("test.db")

    def __init_subclass__(cls, auto_create=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if auto_create:
            try:
                cls.create_table()
            except Exception as e:
                print(f"[auto_create] Could not create table: {e}")

    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    @log_query
    def execute(cls, sql,params=()):
        cursor = cls.connection.cursor()
        cursor.execute(sql,params)
        cls.connection.commit()
        return cursor.fetchall()

    @classmethod
    def get_fields(cls):
        return{
            key:value
            for key,value in cls.__dict__.items()
            if isinstance(value,Field)
        }

    @classmethod
    def create_table(cls):
        name = cls.__name__.lower()

        try:
            columns = cls.get_fields()
            col_definition = ", ".join(f"{col_names} {col_type.sql_type()}" for col_names,col_type in columns.items())
            creation_sql = f"CREATE TABLE {name} ({col_definition})"
            cls.execute(creation_sql)
            print("Table created successfully")
        except sqlite3.OperationalError:
            print("Table already exists")

    @classmethod
    def delete_table(cls):
        name = cls.__name__.lower()
        sql = f"Select name from sqlite_master where type='table' and name='{name}'"
        check_table = cls.execute(sql)
        if check_table:
            drop_sql = f"DROP TABLE {name}"
            cls.execute(drop_sql)
            print(f"Table {name} deleted successfully")
        else:
            print(f"Table {name} not found")

    def save(self):
        name = self.__class__.__name__.lower()
        fields = self.__class__.get_fields()

        attributes = ", ".join(fields.keys())
        placeholder = ", ".join("?" for _ in fields)
        values = [getattr(self,name) for name in fields]

        sql = f"INSERT INTO {name} ({attributes}) VALUES ({placeholder})"

        self.__class__.execute(sql,values)

        print(f"Values inserted successfully in {name}")

    @classmethod
    def get(cls,attributes=None):
        name = cls.__name__.lower()
        if attributes is None:
            sql = f"SELECT * FROM {name}"
        else :
            sql = f"SELECT {attributes} FROM {name}"
        result = cls.execute(sql)
        print(result)

    @classmethod
    def delete(cls,attributes=None):
        name = cls.__name__.lower()
        if attributes is None:
            sql = f"DELETE FROM {name}"
        else:
            sql = f"DELETE FROM {name} WHERE {attributes[0]}=?"
        cls.execute(sql,(attributes[1],))
        print(f"Values deleted successfully in {name} where {attributes[1]}")

    @classmethod
    def get_primary_key(cls):
        for name, field in cls.get_fields().items():
            if "PRIMARY KEY" in field.get_sql_constraints():
                return name,field
        return None,None

    @classmethod
    def filter(cls, condition, attribute, value):
        return QuerySet(cls).filter(condition, attribute, value)

    @classmethod
    def order_by(cls, attribute, order="ASC"):
        return QuerySet(cls).order_by(attribute, order)

    @classmethod
    def group_by(cls, attribute):
        return QuerySet(cls).group_by(attribute)


class QuerySet:
    def __init__(self, model):
        self.model = model
        self.filters = []
        self.order = None
        self.group = None
        self.params = []

    def filter(self, condition, attribute, value):
        self.filters.append(f"{attribute} {condition} ?")
        self.params.append(value)
        return self

    def order_by(self, attribute, order="ASC"):
        self.order = f"{attribute} {order}"
        return self

    def group_by(self, attribute):
        self.group = attribute
        return self

    def _build_sql(self):
        name = self.model.__name__.lower()
        sql = f"SELECT * FROM {name}"

        if self.filters:
            sql += " WHERE " + " AND ".join(self.filters)

        if self.group:
            sql += f" GROUP BY {self.group}"

        if self.order:
            sql += f" ORDER BY {self.order}"

        return sql + ";"

    def fetch(self):
        sql = self._build_sql()
        result = self.model.execute(sql, self.params)
        print(result)
        return result

    def __repr__(self):
        return str(self.fetch())