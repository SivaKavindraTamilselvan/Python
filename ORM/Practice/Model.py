import sqlite3
from ORM.Practice.fields import Field


class Model:

    connection = sqlite3.connect("test.db")
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
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
            if "PRIMARY KEY" in cls.get_fields().items():
                return name,field
        return None

    @classmethod
    def filter(cls,condition,attribute,value):
        name = cls.__name__.lower()
        sql = f"SELECT * FROM {name} WHERE {attribute}{condition}=?"
        result = cls.execute(sql,(value,))
        print(result)