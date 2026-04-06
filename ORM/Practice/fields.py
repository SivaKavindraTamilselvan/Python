class Field:
    def __init__(self, field_type,primary_key= False):
        self.field_type = field_type
        self.primary_key = primary_key

    def sql_type(self):
        return NotImplementedError

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__(int,**kwargs)

    def sql_type(self):
        return "INTEGER"

class CharField(Field):
    def __init__(self, **kwargs):
        super().__init__(str,**kwargs)

    def sql_type(self):
        return "TEXT"
