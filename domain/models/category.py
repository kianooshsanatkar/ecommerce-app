from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ._db import Base
from .entity import Entity


class Category(Entity, Base):
    __tablename__ = 'categories'
    title = Column(String, nullable=False)
    description = Column(String)
    images = Column(String)

    products = relationship('Product', backref='categories')
