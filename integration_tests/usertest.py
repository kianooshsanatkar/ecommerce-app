from dataclasses import dataclass
from unittest import TestCase

from sqlalchemy.orm.session import close_all_sessions

from core.exceptions import AuthenticationException
from domain.models import User
from domain.models import db_Base as Base, DBInitializer
from domain.services import user_validation, email_validation, passwordservice
from domain.services.passwordservice import hashing_password
from handlers import UserHandler


@dataclass
class AddressDTO:
    pass


@dataclass
class UserDTO:
    first_name: str = 'first name'
    last_name: str = 'last name'
    email: str = 'email@domain.tld'
    phone: str = '9121234567'
    addresses = []


class UserTest(TestCase):

    @staticmethod
    def setUpClass():
        UserHandler._Session = DBInitializer.get_session
        UserHandler._user_validation = user_validation
        UserHandler._email_validation = email_validation
        UserHandler._hashing = hashing_password
        UserHandler._password_service = passwordservice

    def setUp(self) -> None:
        Base.metadata.create_all(bind=DBInitializer.get_engine())

    def tearDown(self) -> None:
        close_all_sessions()
        Base.metadata.drop_all(bind=DBInitializer.get_new_engine())

    def test_create_and_get_user(self):
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        uid = UserHandler.create_user(user)
        u = UserHandler.get_user_by_id(uid)
        # assert user properties with origin properties
        self.assertEqual(user.first_name, u.first_name)
        self.assertEqual(user.last_name, u.last_name)
        self.assertEqual(user.phone, u.phone)
        self.assertEqual(user.email, u.email)
        # check if password is null
        self.assertIsNone(u.password)

    def test_create_user_and_get_by_email(self):
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)
        u = UserHandler.get_user_by_email('email@domain.tld')
        # assert user properties with origin properties
        self.assertEqual(user.first_name, u.first_name)
        self.assertEqual(user.last_name, u.last_name)
        self.assertEqual(user.phone, u.phone)
        self.assertEqual(user.email, u.email)
        # check if password is null
        self.assertIsNone(u.password)

