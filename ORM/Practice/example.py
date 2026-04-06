from ORM.Practice.Model import Model
from ORM.Practice.fields import Field,IntegerField,CharField

class User(Model):
    id=IntegerField(PRIMARY_KEY=True)
    name = CharField()
    age = IntegerField()

User.create_table()
b = User(id=2,name="B",age=30).save()
User.get()