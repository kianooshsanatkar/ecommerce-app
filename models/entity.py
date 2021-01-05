from sqlalchemy import Column, Integer

from ._db import Base


class Entity(Base):
    uid = Column(Integer, primary_key=True, unique=True, autoincrement=True)
