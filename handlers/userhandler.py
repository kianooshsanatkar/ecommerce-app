from domain.models import DBInitializer
from domain.models import User
from domain.services import user_validation


class UserHandler:

    Session = DBInitializer.get_session
    user_validation = user_validation

    @classmethod
    def create_user(cls, user: User):
        cls.user_validation(user)
        session = cls.Session()
        session.add(user)
        session.commit()
