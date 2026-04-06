from ORM.Practice.Model import Model
from ORM.Practice.fields import Field,IntegerField,CharField

class User(Model):
    id=IntegerField(primary_key=True)
    name = CharField()
    age = IntegerField()


User.delete_table()