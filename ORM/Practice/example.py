from ORM.Practice.Model import Model
from ORM.Practice.fields import Field,IntegerField,CharField

class User(Model):
    id=IntegerField()
    name = CharField()
    age = IntegerField()


User.get()
User.delete(("name","Siva"))
User.get()