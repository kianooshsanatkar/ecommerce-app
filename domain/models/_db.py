from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class DBInitializer:
    __engine = None
    __Session = None

    def __init__(self):
        pass

    @classmethod
    def get_engine(cls):
        if cls.__engine is None:
            cls.__engine = cls.get_new_engine()
        return cls.__engine

    @classmethod
    def get_new_engine(cls):
        from sqlalchemy import create_engine
        return create_engine('postgresql://numen:pass1234@localhost/NumenDB', echo=False)

    @classmethod
    def get_session(cls) -> Session:
        if cls.__Session is None:
            session = sessionmaker(bind=cls.get_engine())
            cls.__Session = session
        return cls.__Session()
