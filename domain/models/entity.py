from sqlalchemy import Column, Integer


class Entity:
    uid = Column(Integer, primary_key=True, unique=True, autoincrement=True)
