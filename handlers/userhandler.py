from core.exceptions import TypeException
from domain.models import DBInitializer
from domain.models import User
from domain.services import user_validation, email_validation
from domain.services.passwordservice import hashing_password


class UserHandler:
    _Session = DBInitializer.get_session
    _user_validation = user_validation
    _email_validation = email_validation
    _hashing = hashing_password

    @classmethod
    def get_user_by_id(cls, uid: int) -> User:
        if not isinstance(uid, int):
            raise TypeException("uid parameter type must be int!")
        session = cls._Session()
        user = session.query(User).get(uid)
        user.password = None
        return user

    @classmethod
    def get_user_by_email(cls, email: str) -> User:
        if not isinstance(email, str):
            raise TypeException("email parameter type must be string!")
        cls._email_validation(email)
        session = cls._Session()
        user = session.query(User).filter_by(email=email).first()
        user.password = None
        return user

    @classmethod
    def create_user(cls, user: User) -> int:
        if (cls._user_validation(user)):
            user.password = cls._hashing(user.password)
            session = cls._Session()
            session.add(user)
            session.commit()
        return user.uid
