class Field:
    def __init__(self, field_type, **kwargs):
        self.field_type = field_type
        self.constraints = []
        if kwargs.get('primary_key') or kwargs.get('PRIMARY_KEY'):
            self.constraints.append("PRIMARY KEY")
        if kwargs.get('unique'):
            self.constraints.append("UNIQUE")
        if kwargs.get('null') is False:
            self.constraints.append("NOT NULL")

    def get_sql_constraints(self):
        return " ".join(self.constraints)

class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__(int, **kwargs)

    def sql_type(self):
        return f"INTEGER {self.get_sql_constraints()}".strip()

class CharField(Field):
    def __init__(self, **kwargs):
        super().__init__(str, **kwargs)

    def sql_type(self):
        return f"TEXT {self.get_sql_constraints()}".strip()