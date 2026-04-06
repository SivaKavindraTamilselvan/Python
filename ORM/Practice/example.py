from ORM.Practice.Model import Model
from ORM.Practice.fields import Field,IntegerField,CharField,ForeignKeyField

class User(Model):
    id=IntegerField(PRIMARY_KEY=True)
    name = CharField()
    age = IntegerField()

class Book(Model):
    id = IntegerField(PRIMARY_KEY=True)
    author_id = ForeignKeyField(User)
    book_name=CharField()


User.create_table()
Book.create_table()

a=User(id=1,name='Siva Kavindra',age=20).save()
b=User(id=2,name='Kavindra',age=30).save()
c=User(id=3,name='Siva',age=10).save()

d=Book(id=1,author_id=1,book_name='C-Fundamentals').save()
e=Book(id=2,author_id=1,book_name='Java').save()
f=Book(id=3,author_id=2,book_name='Java').save()

User.get()
User.get("age")

User.filter("<","age",25).fetch()
User.filter("=","age",25).fetch()
User.filter("!=","age",20).fetch()

User.order_by("age").fetch()
User.filter("!=","age",20).order_by("age").fetch()

User.delete(("age",20))
User.get()

Book.group_by("book_name").fetch()