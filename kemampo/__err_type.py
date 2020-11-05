import enum
from traceback import format_exc

class ReturnStatus(str, enum.Enum):
    DatabaseError = "Database Error"
    NotFound = "Row Data Not Found"


class KemampoError(Exception):
    def __init__(self, name, identifier, message):
        super().__init__(name, identifier, message)

class SessionError(KemampoError):
    def __init__(self, message):
        err = [i for i in format_exc().splitlines() if "File" in i]
        err = [i for i in err if "kemampo" not in i.lower()]
        err = [i for i in err if "__generic_controller.py" not in i.lower()]
        err = [i for i in err if "__err_type.py" not in i.lower()]

        super().__init__(
            "Database Session Error",
            "@contextmanager.get_session",
            f"Unable to create session. \nCause: {message}"
        )

class QueryKeyInvalid(KemampoError):
    def __init__(self, identifier, message):
        super().__init__("Query Key Invalid", identifier, message)

class QueryLengthInvalid(KemampoError):
    def __init__(self, identifier, message):
        super().__init__("Query Length Invalid", identifier, message)
