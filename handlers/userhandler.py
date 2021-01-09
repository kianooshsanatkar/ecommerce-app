from core.exceptions import ValueException, TypeException
from domain.models import DBInitializer
from domain.models import User
from domain.services import user_validation, email_validation


class UserHandler:

    Session = DBInitializer.get_session
    user_validation = user_validation
    email_validation = email_validation

    @classmethod
    def get_user_by_id(cls, uid: int) -> User:
        if not isinstance(uid, int):
            raise TypeException("uid parameter type must be int!")
        session = cls.Session()
        return session.query(User).get(uid)

    @classmethod
    def get_user_by_email(cls, email: str) -> User:
        if not isinstance(email, str):
            raise TypeException("email parameter type must be string!")
        cls.email_validation(email)
        session = cls.Session()
        return session.query(User).filter_by(email=email).first()

    @classmethod
    def create_user(cls, user: User) -> int:
        cls.user_validation(user)
        session = cls.Session()
        session.add(user)
        session.commit()
        return user.uid
