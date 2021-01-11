from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ._db import Base
from .entity import Entity


class User(Base, Entity):
    __tablename__ = 'users'
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True)
    phone = Column(String, unique=True)
    password = Column(String, nullable=False)
    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return User.__name__ + "('" + self.first_name + "', '" + self.last_name + "', '" \
               + self.phone + "', '" + self.email + "', " + str(self.uid) + ")"


class Address(Entity, Base):
    __tablename__ = 'addresses'
    province = Column(String, nullable=False)
    city = Column(String, nullable=False)
    zip_code = Column(String, nullable=True)
    postal_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.uid'))
    user = relationship('User', back_populates='addresses')

    # user = relationship("user", back_populates="addresses")

    def __repr__(self):
        # return f"{self.__class__.__name__}('{self.provinces}', '{self.city}', '{self.zip_code}', " \
        #        f"'{self.postal_address}', {self.user_id})"
        return "%r(%r, %r, %r, %r, %r, %r)" % (self.__class__.__name__, self.uid, self.province, self.city,
                                               self.zip_code, self.postal_address, self.user_id)
