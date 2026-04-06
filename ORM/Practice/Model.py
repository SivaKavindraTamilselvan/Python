import sqlite3
from multiprocessing import connection


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
    def check(cls):
        result = cls.execute("SELECT name from sqlite_master where type='table';")
        print(result)

