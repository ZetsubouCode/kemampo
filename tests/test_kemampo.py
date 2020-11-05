from sqlalchemy.orm import sessionmaker
from kemampo import Kemampo

from . import DB_ENGINE, Account


kemampo = Kemampo(sessionmaker(bind=DB_ENGINE))
AccountController = kemampo.create_controller(Account)

def test_constructor():
    assert isinstance(Kemampo, type)

def test_constructed():
    assert isinstance(kemampo, Kemampo)

def test_if_create_controller_exist():
    assert bool(kemampo.create_controller)

def test_generated_controller():
    assert AccountController.__name__ == "AccountController"
    assert AccountController.__class__.__name__ == "AccountController"

def test_controller_has_add():
    assert bool(AccountController.add)

def test_controller_has_get():
    assert bool(AccountController.get)

def test_controller_has_get_all():
    assert bool(AccountController.get_all)

def test_controller_has_update_by_id():
    assert bool(AccountController.update_by_id)

def test_controller_has_delete():
    assert bool(AccountController.delete)
