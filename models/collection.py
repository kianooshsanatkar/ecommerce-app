from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .entity import Entity


class Collection(Entity):
    __tablename__ = 'collections'
    title = Column(String, nullable=False)
    images = Column(String)
    description = Column(String)

    products = relationship("Product", backref="collections")
