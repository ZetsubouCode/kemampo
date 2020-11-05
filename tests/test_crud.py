import random
from typing import Tuple, Dict, Any

from sqlalchemy.orm.session import sessionmaker
from kemampo import Kemampo, ReturnStatus

from . import DB_ENGINE, Account

kemampo = Kemampo(sessionmaker(bind=DB_ENGINE))
AccountController = kemampo.create_controller(Account)

def __name_generator(length: int = -1) -> str:
    return "".join(
        [
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[random.randint(0, 61)]
            for _ in range(
                length if length > 0 else random.randint(9, 18)
            )
        ]
    )

def test_add() -> Tuple[str, Dict[str, Any]]:
    rname = __name_generator(9)
    status, data = AccountController.add(**{"name": rname})
    if status:
        assert isinstance(data, dict)
        assert 'id' in data
        assert isinstance(data["id"], int)
        assert 'name' in data
        assert isinstance(data["name"], str)
        assert rname in data.values()
    else:
        assert data == ReturnStatus.DatabaseError

    return rname, data.value if isinstance(data, ReturnStatus) else data

def test_get():
    name, data = test_add()
    status, datass = AccountController.get(id=data["id"])
    if not status:
        assert False, "Failed to Add!"

    for i in datass:
        assert isinstance(i, dict)
        assert "id" in i
        assert "name" in i
        assert i["id"] == data["id"]
        assert i["name"] == name

def test_get_all():
    status, data = AccountController.get_all()

    assert isinstance(data, list)
    for i in data:
        assert isinstance(i, dict)
        assert "id" in i
        assert "name" in i

def test_update_by_id():
    _, data = test_add()
    new_name = __name_generator()
    status, result = AccountController.update_by_id(data["id"], **{"name": new_name})

    assert isinstance(result, dict)
    assert "id" in result
    assert "name" in result
    assert result["name"] == new_name

def test_delete():
    new_name = eval("__name_generator(20)")
    _, data = eval("AccountController.add(**{\"name\": new_name})")
    if not isinstance(data, dict):
        assert False, "Failed to add data"

    nid = data["id"]
    nname = data["name"]

    status, ddata = eval("AccountController.delete(id=nid)")
    if not isinstance(ddata, dict):
        assert False, "Failed to delete data"

    assert ddata["id"] == nid
    assert ddata["name"] == nname

    _, result = AccountController.get_all()
    values = []
    for i in result:
        [values.append(j) for j in i.values()]

    assert nid not in values
    assert nname not in values
