from ORM.Practice.Model import Model
from ORM.Practice.fields import Field,IntegerField,CharField
from ORM.orm import ForeignKey


class User(Model):
    id=IntegerField(PRIMARY_KEY=True)
    name = CharField()
    age = IntegerField()

User.create_table()
User.get()

class Book(Model):
    id = IntegerField(PRIMARY_KEY=True)
    author_name = ForeignKey(User)
    book_name=CharField()

User.filter("<","age",26)