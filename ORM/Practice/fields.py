class Field:

    def __init__(self, field_type, **kwargs):
        self.field_type = field_type
        self.name = None          # filled in by __set_name__
        self.constraints = []
        if kwargs.get('primary_key') or kwargs.get('PRIMARY_KEY'):
            self.constraints.append("PRIMARY KEY")
        if kwargs.get('unique'):
            self.constraints.append("UNIQUE")
        if kwargs.get('null') is False:
            self.constraints.append("NOT NULL")


    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"   # instance-level storage key

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.storage_name)

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError(
                f"Field '{self.name}' expects {self.field_type.__name__}, "
                f"got {type(value).__name__}"
            )
        instance.__dict__[self.storage_name] = value


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


class ForeignKeyField(Field):

    def __init__(self, reference_model, **kwargs):
        super().__init__(int, **kwargs)          # FK values are integers
        self.reference_model = reference_model

    def __set__(self, instance, value):
        if value is not None and isinstance(value, self.reference_model):
            pk_name, _ = self.reference_model.get_primary_key()
            value = getattr(value, pk_name)
        super().__set__(instance, value)

    def sql_type(self):
        pk_name, pk_field = self.reference_model.get_primary_key()

        base_type = pk_field.sql_type().split()[0]          # e.g. "INTEGER"
        ref_table = self.reference_model.__name__.lower()

        return f"{base_type} REFERENCES {ref_table}({pk_name})".strip()