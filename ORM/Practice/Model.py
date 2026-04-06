import sqlite3
from ORM.Practice.fields import Field


class Model:

    connection = sqlite3.connect("test.db")
    def __init__(self):
        for key, value in self.__dict__.items():
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