from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ._db import Base
from .entity import Entity


class User(Base, Entity):
    __tablename__ = 'users'
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, unique=True)
    email = Column(String, unique=True)
    addresses = relationship("Address", backref="users")

    def __repr__(self):
        return User.__name__ + "('" + self.first_name + "', '" + self.last_name + "', '" \
               + self.phone + "', '" + self.email + "', " + str(self.uid) + ")"


class Address(Entity, Base):
    __tablename__ = 'addresses'
    provinces = Column(String, nullable=False)
    city = Column(String, nullable=False)
    zip_code = Column(String, nullable=True)
    postal_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.uid'))
    # user = relationship("user", back_populates="addresses")
