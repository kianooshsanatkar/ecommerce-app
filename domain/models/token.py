from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from domain.models._db import Base
from domain.models.entity import Entity


class Token(Entity, Base):
    __tablename__ = 'tokens'
    token_hex = Column(String, nullable=False)
    token_url = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.uid'), nullable=False)
    user = relationship('User', backref='tokens')
    requested_time = Column(DateTime, nullable=False)
    used_time = Column(DateTime, nullable=False)
