## TASK3
Custom ORM (Object-Relational Mapper)

## Objective

Design a lightweight ORM from scratch using Python metaclasses and descriptors. Support model definition, field validation, query building, relationships, and lazy loading.

## 📋 Requirements

- [x]  Python metaclasses (`__new__`, `__init_subclass__`)
- [x]  Descriptor protocol (`__get__`, `__set__`, `__set_name__`)
- [x]  Decorators and class decorators
- [x]  SQL syntax (DDL + DML)
- [x]  `sqlite3` standard library module
- [x]  Method chaining pattern

## 💡 Use-Case

- [x]  Define database tables as Python classes with typed fields
- [x]  Auto-generate `CREATE TABLE` SQL from class definitions
- [x]  CRUD operations via `.save()`, `.delete()`, `.filter()`
- [x]  Support `ForeignKey` relationships with lazy-loaded access
- [x]  Chain queries: `User.filter(age__gte=25).order_by("-name").all()`

## SCREENSHOTS

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/b57c7b3c-5bd6-412d-88a8-bf1639645f05" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7a1d92a1-9e4b-4d53-87ed-1b4aeb47e35f" />

