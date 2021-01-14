from domain.models import DBInitializer
from domain.services import user_validation, email_validation, passwordservice, address_validation, phone_validation
from handlers import UserHandler
from handlers.addresshandler import AddressHandler
from handlers.tokenhandler import TokenHandler


def reset_user_handler_injection():
    UserHandler._Session = DBInitializer.get_session
    UserHandler._user_validation = user_validation
    UserHandler._email_validation = email_validation
    UserHandler._hashing = passwordservice.hashing_password
    UserHandler._password_service = passwordservice
    UserHandler._phone_validation = phone_validation


def reset_address_handler_injection():
    AddressHandler._Session = DBInitializer.get_session
    AddressHandler._address_validation = address_validation


def reset_token_handler_injection():
    TokenHandler._Session = DBInitializer.get_session
    TokenHandler._get_user = UserHandler.get_user_by_id
