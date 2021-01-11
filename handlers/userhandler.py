from core.exceptions import TypeException, AuthenticationException, ValueException, SecurityException
from domain.models import DBInitializer
from domain.models import User
from domain.models.user import Address
from domain.services import user_validation, email_validation, phone_validation, passwordservice, address_validation


class UserHandler:
    _Session = DBInitializer.get_session
    _user_validation = user_validation
    _email_validation = email_validation
    _phone_validation = phone_validation
    _password_service = passwordservice
    _hashing = _password_service.hashing_password
    _address_validation = address_validation

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
        if cls._user_validation(user):
            user.password = cls._hashing(user.password)
            session = cls._Session()
            session.add(user)
            session.commit()
        return user.uid

    @classmethod
    def log_in_by_email(cls, email: str, password: str) -> User:
        if cls._email_validation(email):
            session = cls._Session()
            user = session.query(User).filter_by(email=email).first()
            if not user:
                raise AuthenticationException("Wrong Email Address!")
            if cls._password_service.password_verification(user.password, password):
                user.password = None
                return user
            raise AuthenticationException("Wrong Password!")
        raise ValueException("Invalid email address value!")

    @classmethod
    def log_in_by_phone(cls, phone: str, password: str) -> User:
        if cls._phone_validation(phone):
            session = cls._Session()
            user = session.query(User).filter_by(phone=phone).first()
            if not user:
                raise AuthenticationException("Wrong Phone Number!")
            if cls._password_service.password_verification(user.password, password):
                user.password = None
                return user
            raise AuthenticationException("Wrong Password!")
        raise ValueException("Invalid phone value!")

    @classmethod
    def update_user_info(cls, uid: int, first_name: str = None, last_name: str = None) -> User:
        session = cls._Session()
        user = session.query(User).get(uid)
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        session.commit()
        user.password = None
        return user

    @classmethod
    def add_address(cls, uid, address: Address):
        session = cls._Session()
        user = session.query(User).get(uid)
        if not user:
            raise ValueException(f"there is no user with this id: {uid}")
        cls._address_validation(address)
        user.addresses.append(address)
        session.commit()
        return True

    @classmethod
    def get_address_by_id(cls, uid):
        session = cls._Session()
        return session.query(Address).get(uid)

    @classmethod
    def change_password(cls, user_id, old_password, new_password):
        session = cls._Session()
        user = session.query(User).get(user_id)
        if not user:
            raise SecurityException("User doesn't exist!")
        if not cls._password_service.password_verification(user.password, old_password):
            raise AuthenticationException("Wrong Password!")
        if not cls._password_service.password_validation(new_password):
            raise ValueException("Entered password is not valid!")
        pss = cls._password_service.hashing_password(new_password)
        user.password = pss
        session.commit()
        return True
