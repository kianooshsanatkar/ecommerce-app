from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ._db import Base
from .entity import Entity


class User(Entity, Base):
    __tablename__ = 'users'
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, unique=True)
    email = Column(String, unique=True)
    addresses = relationship("Address", backref="users")


class Address(Entity, Base):
    __tablename__ = 'addresses'
    provinces = Column(String, nullable=False)
    city = Column(String, nullable=False)
    zip_code = Column(String, nullable=True)
    postal_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.uid'))
    # user = relationship("user", back_populates="addresses")
