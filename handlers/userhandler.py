from core.exceptions import TypeException, AuthenticationException, ValueException, SecurityException
from domain.models import DBInitializer
from domain.models import User
from domain.models.token import ExchangeMethods
from domain.services import user_validation, email_validation, phone_validation, passwordservice
from domain.services.userservices import get_user_state
from handlers.tokenhandler import TokenHandler


class UserHandler:
    _Session = DBInitializer.get_session
    _user_validation = user_validation
    _email_validation = email_validation
    _phone_validation = phone_validation
    _password_service = passwordservice
    _hashing = _password_service.hashing_password
    _get_user_state = get_user_state

    _hex_token_verification = TokenHandler.hexadecimal_token_validation
    _url_token_verification = TokenHandler.url_token_validation
    _generate_token = TokenHandler.generate_token

    @classmethod
    def get_user_by_id(cls, uid: int) -> User:
        if not isinstance(uid, int):
            raise TypeException("uid parameter type must be int!")
        session = cls._Session()
        u = session.query(User).get(uid)
        if not u:
            raise ValueException(f"user with this id <{uid}> doesn't exist!")
        u.password = None
        return u

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
            user.state = cls._get_user_state(user).value
            session = cls._Session()
            session.add(user)
            session.commit()
            if user.email:
                cls._generate_token(user.uid, ExchangeMethods.EMAIL)
            if user.phone:
                cls._generate_token(user.uid, ExchangeMethods.PHONE)
        return user.uid

    @classmethod
    def verify_user_email_by_hex_token(cls, user_id: int, hex_token: str):
        session = cls._Session()
        user = session.query(User).get(user_id)
        if user.is_email_verified:
            return True
        if not TokenHandler.hexadecimal_token_validation(user_id, hex_token, ExchangeMethods.EMAIL):
            return False
        user.is_email_verified = True
        user.state = get_user_state(user).value
        session.commit()

    @classmethod
    def verify_user_phone_by_hex_token(cls, user_id: int, hex_token: str):
        session = cls._Session()
        user = session.query(User).get(user_id)
        if user.is_phone_verified:
            return True
        if not TokenHandler.hexadecimal_token_validation(user_id, hex_token, ExchangeMethods.PHONE):
            return False
        user.is_phone_verified = True
        user.state = get_user_state(user).value
        session.commit()

    @classmethod
    def verify_user_exchange_method_by_url_token(cls, url_token: str):
        user_id, ex_method = TokenHandler.url_token_validation(url_token)
        session = cls._Session()
        user = session.query(User).get(user_id)
        if ex_method == ExchangeMethods.PHONE.value:
            user.is_phone_verified = True
        elif ex_method == ExchangeMethods.EMAIL.value:
            user.is_email_verified = True
        user.state = cls._get_user_state(user).value
        session.commit()

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

    @classmethod
    def change_password_by_hex_token(cls, user_id, hex_token, new_password):
        if not passwordservice.password_validation(new_password):
            raise ValueException("Password is not valid!")
        if cls._hex_token_verification(user_id, hex_token):
            session = cls._Session()
            user = session.query(User).get(user_id)
            user.password = cls._password_service.hashing_password(new_password)
            session.commit()
            return True
        raise SecurityException("Token is not valid!")

    @classmethod
    def change_password_by_url_token(cls, url_token, new_password):
        if not passwordservice.password_validation(new_password):
            raise ValueException("Password is not valid!")
        user_id, _ = cls._url_token_verification(url_token)
        session = cls._Session()
        user = session.query(User).get(user_id)
        user.password = passwordservice.hashing_password(new_password)
        session.commit()
        return True
