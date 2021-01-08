from sqlalchemy import Column, String, Integer, Float, ForeignKey

from .entity import Entity


class Product(Entity):
    __tablename__ = 'products'
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    Images = Column(String)
    price = Column(Float, nullable=False)
    discount = Column(Float, nullable=False)

    collection_id = Column(Integer, ForeignKey('collections.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
