from datetime import timedelta, datetime
from enum import Enum

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from domain.models._db import Base
from domain.models.entity import Entity

TIME_SPAN = timedelta(hours=1)


class ExchangeMethods(Enum):
    PHONE = 1
    EMAIL = 2


class Token(Entity, Base):
    __tablename__ = 'tokens'
    hex_token = Column(String, nullable=False)
    url_token = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.uid'), nullable=False)
    user = relationship('User', backref='tokens')
    requested_time = Column(DateTime, nullable=False, default=datetime.utcnow())
    time_limit = Column(DateTime, nullable=False, default=datetime.utcnow() + TIME_SPAN)
    failed_attempts = Column(Integer, nullable=False, default=0)
    last_used_time = Column(DateTime, nullable=True)
    deactivate = Column(Boolean, nullable=False, default=False)
    exchange_method = Column(Integer, nullable=True)

    def __repr__(self):
        return ("Token(%r, %r, %r, %r, %r)"
                % (self.user_id, self.requested_time, self.failed_attempts, self.last_used_time, self.deactivate))
