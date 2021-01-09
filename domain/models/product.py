from sqlalchemy import Column, String, Integer, Float, ForeignKey

from ._db import Base
from .entity import Entity


class Product(Entity, Base):
    __tablename__ = 'products'
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    Images = Column(String)
    price = Column(Float, nullable=False)
    discount = Column(Float, nullable=False)

    collection_id = Column(Integer, ForeignKey('collections.uid'))
    category_id = Column(Integer, ForeignKey('categories.uid'))
