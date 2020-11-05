<h1 align=center> Kemampo </h1>
<i><p align=center>Small, Lightweight Library to cut down SQLAlchemy Controllers Boilerplates</p></i>

<h2 align=center> Usage </h2>

### Concept

1. First define all of your tables, and all things necessary
2. instead of implementing custom Controllers that handle errors and what not. you can use Kemampo to cut downs all of the Boilerplates. so all you need to do next is: implement sqlalchemy's `sessionmaker` and pass it into Kemampo intializer
4. use Kemampo to generate all the basic **_CRUD_** controllers.
5. Use it as is. or add it to your custom Controller class using `setattr`

### Example
Define your table
```python
DB_ENGINE = create_engine(
    "sqlite:///",
    pool_pre_ping=True,
    echo=False,
)

DB_BASE = declarative_base(bind=DB_ENGINE)
metadata = DB_BASE.metadata

class User(DB_BASE):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(16), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
```

Use Kemampo
```python
from kemampo import Kemampo

kemampo = Kemampo(sessionmaker(bind=DB_ENGINE))
UserController = kemampo.generate_controller(User)

user_data = {"username": "test_new_user", "password": "a_password_hash"}
update_user_data = {"username": "updated_username"}
status, user = UserController.add(**new_user_data)                  # create new user
status, users = UserController.get(id=1)                            # get by id
status, user = UserController.update_by_id(1, **update_user_data)   # update by id
status, users = UserController.get_all()                            # get all
status, user = UserController.delete(1)                             # delete by id
```



<h2 align=center> Installation </h2>

You can install via PyPI

```bash
python3 -m pip install kemampo
```

<h2 align=center> API Documentations </h2>

### `kemampo.Kemampo(session_maker, log_callback)`
- Constructor
    - `sessionmaker`
        - Expected Type: `sqlalchemy.orm.session.sessionmaker`
        - Your own sessionmaker. docs: https://docs.sqlalchemy.org/en/13/orm/session_api.html#session-and-sessionmaker
    - `log_callback`
        - Expected Type: `Callbacks` or `function`
        - put your function here to get kemampo logging output
- Methods
    - `Kemampo.generate_controller(target_model)`
        - The Main feature of kemampo, create a **_CRUD_** controller for `target_model`
        - `target_model`
            - Expected Type: _your table_ specifically `sqlalchemy.ext.declarative.DeclarativeMeta` or it's subclass
            - returns `<table-name>Controller`
### `<table-name>Controller`
The core feature of Kemampo, provide you with basic **_CRUD_** Controller Operations
- Methods
    - `add(**table_dict_model)`
        - Add new row data to database
        - `table_dict_model`
            - type: `Dict`
            - scheme:
                ```python
                {table_column_name: column_name_value, ...}
                ```
        - returns Tuple of:
            - (`True`, `added_dict_of_model`) or
            - (`False`, `ReturnStatus`)
    - `get(**target_row_column_key_value)`
        - Get rows data from database, based on column name you give with certain value. support multiple column name and value
        - `target_row_column_key_value`
            - type: `Dict`
            - scheme:
                ```python
                {table_column_name: column_name_value, ...}
                ```
        - returns Tuple of:
            - (`True`, `List[dict_of_model]`) or
            - (`False`, `ReturnStatus`)
    - `get_all()`
        - Gather all row values from database
        - returns Tuple of:
            - (`True`, `List[dict_of_model]`) or
            - (`False`, `ReturnStatus`)
    - `update_by_id(target_id, **updated_row_column_key_value)`
        - `target_id`
            - type: `int`
        - `updated_row_column_key_value`
            - type: `Dict`
            - scheme:
                ```python
                {table_column_name: column_name_value, ...}
                ```
        - returns Tuple of:
            - (`True`, `dict_of_model`) or
            - (`False`, `ReturnStatus`)
    - `delete(**target_row_column_key_value)`
        - `target_row_column_key_value`
            - type: `Dict`
            - scheme:
                ```python
                {table_column_name: column_name_value, ...}
                ```
        - returns Tuple of:
            - (`True`, `dict_of_model`) or
            - (`False`, `ReturnStatus`)

### `ReturnStatus`

an Enumeration of possible Errors happening inside Kemampo

- `ReturnStatus.DatabaseError`
    - Error happened internally
    - Values: `str` -> `"Database Error"`
- `ReturnStatus.NotFound`
    - Targeted row data was not found inside database
    - Values: `str` -> `"Row Data Not Found"`
