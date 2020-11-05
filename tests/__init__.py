from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import BigInteger

DB_ENGINE = create_engine(
    "sqlite:///",
    pool_pre_ping=True,
    echo=False,
)

DB_BASE = declarative_base(bind=DB_ENGINE)
metadata = DB_BASE.metadata

class Account(DB_BASE):
    __tablename__ = 'account'
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

metadata.create_all(DB_ENGINE)
