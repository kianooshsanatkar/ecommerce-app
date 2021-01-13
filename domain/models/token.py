from datetime import timedelta, datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from domain.models._db import Base
from domain.models.entity import Entity

TIME_SPAN = timedelta(hours=1)


class Token(Entity, Base):
    __tablename__ = 'tokens'
    hex_token = Column(String, nullable=False)
    url_token = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.uid'), nullable=False)
    user = relationship('User', backref='tokens')
    requested_time = Column(DateTime, nullable=False)
    time_limit = Column(DateTime, nullable=False, default=datetime.utcnow() + TIME_SPAN)
    failed_attempts = Column(Integer, nullable=False, default=0)
    last_used_time = Column(DateTime, nullable=True)
    deactivate = Column(Boolean, nullable=False, default=False)
