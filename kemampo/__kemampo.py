from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import session
from sqlalchemy.orm.scoping import scoped_session

from contextlib import contextmanager
from typing import Any, Generator, ContextManager, Callable

from .__err_type import SessionError

from sqlalchemy import Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.inspection import inspect

from contextlib import contextmanager
from typing import Union, Tuple, Dict, List, Any, ContextManager, Callable

from .__err_type import ReturnStatus
from .__err_type import QueryKeyInvalid, QueryLengthInvalid


class GenericController:
        # TODO: Implement using __dict__ as opposed to to_dict(), then remove the _sa_instance
        __name__ = "GENERIC_CONTROLLER"

        def __init__(self, table_model: DeclarativeMeta):
            self.session_generator: Callable[..., ContextManager[Session]]
            self.target_model: DeclarativeMeta = table_model
            self.target_model_name: str = table_model.__name__
            self.target_model_columns = [i.name for i in inspect(self.target_model).columns]
            self.target_model_primary_keys = [i for i in inspect(self.target_model).primary_key]

        def __compare_kwargs_to_column(self, target_kwargs: Dict, position):
            for key in target_kwargs:
                if key not in self.target_model_columns:
                    raise QueryKeyInvalid(
                        f"{self.target_model_name}.{position}",
                        f"key {key} was not a valid {self.target_model_name} Column",
                    )

        def __compare_kwargs_length_to_column_length(self, target_kwargs: Dict, position):
            if len(target_kwargs) > len(self.target_model_columns):
                raise QueryLengthInvalid(
                    f"{self.target_model_name}.{position}",
                    f"Length of provided column query is longer than {self.target_model} column count! "
                    f"len({target_kwargs}) >= len({self.target_model_columns})",
                )

        def __truncate_sa_instance_from_model(self, model_dictionary: Dict) -> Dict[str, Any]:
            nd: Dict = dict()
            for i in model_dictionary:
                if i in self.target_model_columns:
                    nd.update({i: model_dictionary[i]})
            try: del nd['_sa_instance_state']
            except: ...

            return nd

        def add(self, **kwargs) -> Tuple[bool, Union[Dict[str, Any], ReturnStatus]]:
            self.__compare_kwargs_to_column(kwargs, "add")
            self.__compare_kwargs_length_to_column_length(kwargs, "add")

            with self.session_generator() as sess:
                model = self.target_model(**kwargs)
                sess: Session
                try:
                    sess.add(model)
                    sess.commit()
                    sess.flush()
                    sess.refresh(model)
                except Exception as e:
                    sess.rollback()
                    print(e)
                    return False, ReturnStatus.DatabaseError  # Database Failure
                return True, self.__truncate_sa_instance_from_model(model.__dict__)

        def get(self, **target) -> Tuple[bool, List[Dict[str, Any]]]:
            self.__compare_kwargs_to_column(target, "get")
            self.__compare_kwargs_length_to_column_length(target, "get")

            with self.session_generator() as sess:
                result = [self.__truncate_sa_instance_from_model(i.__dict__) for i in sess.query(self.target_model).filter_by(**target).all()]
                return (bool(result), result if result else [])

        def get_all(self) -> Tuple[bool, List[Dict[str, Any]]]:
            with self.session_generator() as sess:
                result = [self.__truncate_sa_instance_from_model(i.__dict__) for i in sess.query(self.target_model).all()]
                return (True, result) if result else (False, [])

        def update_by_id(self, target_id: int, **new_data) -> Tuple[bool, Union[ReturnStatus, Dict[str, Any]]]:
            # TODO: replace this with more sophisticated more broad targeting instead of just ID
            self.__compare_kwargs_to_column(new_data, "update_by_id")
            self.__compare_kwargs_length_to_column_length(new_data, "update_by_id")

            with self.session_generator() as sess:
                target_data = sess.query(self.target_model).filter_by(id=target_id).first()
                if not target_data:
                    return False, ReturnStatus.NotFound

                try:
                    sess.query(self.target_model).filter_by(id=target_id).update(new_data)
                    sess.commit()
                    sess.flush()
                    sess.refresh(target_data)
                except Exception as e:
                    return False, ReturnStatus.DatabaseError
                return True, self.__truncate_sa_instance_from_model(target_data.__dict__)

        def delete(self, **target) -> Union[Tuple[bool, ReturnStatus], Tuple[bool, Dict[str, Any]]]:
            self.__compare_kwargs_to_column(target, "delete")
            if len([i for i in target]) > 1:
                raise QueryLengthInvalid(f"{self.target_model_name}.delete", "Length Of Target is more than one")

            e = ""
            ee = ""
            with self.session_generator() as sess:
                sess: Session
                result = sess.query(self.target_model).filter_by(**target).first()
                if not result:
                    return False, ReturnStatus.NotFound
                result_dict = result.__dict__
                result_dict = self.__truncate_sa_instance_from_model(result_dict)

                result = sess.query(self.target_model).filter_by(**target)
                try:
                    result.delete()
                    sess.commit()
                    sess.flush()
                except Exception as e:
                    e = f"{e}"
                    ee = ""
                    try:
                        sess.delete(result)
                        sess.commit()
                        sess.flush()
                    except Exception as ee:
                        sess.rollback()
                        return False, ReturnStatus.DatabaseError
                    e = f"{e} | {ee}"

            return True, result_dict

def _KEMAMPO_DEFAULT_LOG(message):
    ...

class Kemampo:
    session_generator: Callable[..., ContextManager[Session]]
    __log: Callable[..., Any]

    def __init__(self, session_maker: sessionmaker, log_callback: Callable[..., Any] = _KEMAMPO_DEFAULT_LOG):
        if not isinstance(session_maker, sessionmaker):
            log_callback(f"Parameter session_maker expected to have type of sqlalchemy.orm.sessionmaker not {type(session_maker)}")
            raise ValueError(f"Parameter session_maker expected to have type of sqlalchemy.orm.sessionmaker not {type(session_maker)}")

        SESS_MAKER = session_maker
        @contextmanager
        def __get_session() -> Generator[Session, None, None]:
            session = None
            try:
                csession = scoped_session(SESS_MAKER)
                session = csession()

                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                raise SessionError(e)
            finally:
                if session:
                    session.close()

        self.__log = log_callback
        self.session_generator: Callable[..., ContextManager[Session]] = __get_session

    def create_controller(self, target_model: DeclarativeMeta):
        self.__log("Instantiating Generic Controller")
        generic_controller = GenericController(target_model)

        # add logger to Generic Controller
        setattr(generic_controller, "__log", self.__log)

        # Add Session generator to Generic Controller
        self.__log("Setting Session Generator for Generic Controller")
        setattr(generic_controller, "session_generator", self.session_generator)

        # Setting Generic Controller classname
        self.__log(f"Setting Generic Controller classname to {target_model.__name__}Controller")
        setattr(generic_controller.__class__, "__name__", f"{target_model.__name__}Controller")

        # Setting Generic Controller name
        self.__log(f"Setting Generic Controller name to {target_model.__name__}Controller")
        setattr(generic_controller, "__name__", f"{target_model.__name__}Controller")

        # return generic_controller
        return generic_controller


__all__ = ["Kemampo"]
