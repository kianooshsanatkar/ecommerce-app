from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ._db import Base
from .entity import Entity


class Collection(Entity, Base):
    __tablename__ = 'collections'
    title = Column(String, nullable=False)
    images = Column(String)
    description = Column(String)

    products = relationship("Product", backref="collections")
