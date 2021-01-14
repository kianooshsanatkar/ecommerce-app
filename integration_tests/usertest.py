from dataclasses import dataclass
from unittest import TestCase

from sqlalchemy.orm.session import close_all_sessions

from core.exceptions import AuthenticationException, ValueException, SecurityException
from domain.models import User, Token
from domain.models import db_Base as Base, DBInitializer
from domain.models.user import Address
from domain.services import user_validation, email_validation, passwordservice
from domain.services.passwordservice import hashing_password
from handlers import UserHandler
from handlers.tokenhandler import TokenHandler, TokenVia


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

        # reset token dependencies
        TokenHandler._Session = DBInitializer.get_session
        TokenHandler._get_user = UserHandler.get_user_by_id

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

    def test_log_in_by_email(self):
        pss = 'Pa$$w0rd'
        user = User(password=pss, first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)

        # region check failed scenario
        with self.assertRaises(AuthenticationException) as _ex:
            UserHandler.log_in_by_email(user.email, user.password)
        with self.assertRaises(AuthenticationException) as _ex:
            UserHandler.log_in_by_email(user.email, 'wrong password')
        self.assertEqual('Entered password is wrong!', str(_ex.exception))
        with self.assertRaises(AuthenticationException) as _ex:
            UserHandler.log_in_by_email('wrong_email@domain.tld', pss)
        self.assertEqual('Wrong Email Address!', str(_ex.exception))
        # endregion

        # region check succeed scenario
        u = UserHandler.log_in_by_email(user.email, pss)
        # assert user properties with origin properties
        self.assertEqual(user.first_name, u.first_name)
        self.assertEqual(user.last_name, u.last_name)
        self.assertEqual(user.phone, u.phone)
        self.assertEqual(user.email, u.email)
        # check if password is null
        self.assertIsNone(u.password)
        # endregion

    def test_log_in_by_phone(self):
        pss = 'Pa$$w0rd'
        user = User(password=pss, first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)

        # region check failed scenario
        with self.assertRaises(AuthenticationException) as _ex:
            UserHandler.log_in_by_phone(user.phone, user.password)
        with self.assertRaises(AuthenticationException) as _ex:
            UserHandler.log_in_by_phone(user.phone, 'wrong password')
        self.assertEqual('Entered password is wrong!', str(_ex.exception))
        with self.assertRaises(AuthenticationException) as _ex:
            UserHandler.log_in_by_phone('9121234561', pss)
        self.assertEqual('Wrong Phone Number!', str(_ex.exception))
        # endregion

        # region check succeed scenario
        u = UserHandler.log_in_by_phone(user.phone, pss)
        # assert user properties with origin properties
        self.assertEqual(user.first_name, u.first_name)
        self.assertEqual(user.last_name, u.last_name)
        self.assertEqual(user.phone, u.phone)
        self.assertEqual(user.email, u.email)
        # check if password is null
        self.assertIsNone(u.password)
        # endregion

    def test_user_change_info(self):
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)
        u = UserHandler.update_user_info(user.uid, 'new name', 'new last name')
        self.assertEqual('new name', u.first_name)
        self.assertEqual('new last name', u.last_name)

    def test_add_address_to_user_addresses(self):
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)

        # region Succeed Scenario
        address = Address(province='tehran', city='tehran', zip_code='1' * 10,
                          postal_address='somewhere in tehran')
        result = UserHandler.add_address(user.uid, address)
        self.assertTrue(result)
        add = UserHandler.get_address_by_id(address.uid)
        self.assertEqual(address.province, add.province)
        self.assertEqual(address.city, add.city)
        self.assertEqual(address.zip_code, add.zip_code)
        self.assertEqual(address.postal_address, add.postal_address)
        # endregion

        # region Failed Scenario
        new_address = Address(city='tehran', zip_code='1' * 10,
                              postal_address='somewhere in tehran')
        with self.assertRaises(ValueException):
            UserHandler.add_address(user.uid, new_address)

        new_address = Address(province='tehran', zip_code='1' * 10,
                              postal_address='somewhere in tehran')
        with self.assertRaises(ValueException):
            UserHandler.add_address(user.uid, new_address)

        new_address = Address(province='tehran', city='tehran', zip_code='0123456789')
        with self.assertRaises(ValueException):
            UserHandler.add_address(user.uid, new_address)

        new_address = Address(province='tehran', city='tehran', postal_address='somewhere in tehran')
        with self.assertRaises(ValueException) as _ex:
            UserHandler.add_address(12345, new_address)
        self.assertEqual("there is no user with this id: 12345", str(_ex.exception))
        # endregion

    def test_change_password(self):
        pss = 'Pa$$w0rd'
        user = User(password=pss, first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)

        # region check failed scenario
        with self.assertRaises(SecurityException) as _ex:
            UserHandler.change_password(0, pss, 'Pa$$w)rd1')
            self.assertEqual("user doesn't exist!", str(_ex.exception))
        with self.assertRaises(AuthenticationException) as _ex:
            UserHandler.change_password(user.uid, 'another Pa$$w0rd', 'Pa$$w)rd1')
        self.assertEqual('Entered password is wrong!', str(_ex.exception))
        with self.assertRaises(ValueException) as _ex:
            UserHandler.change_password(user.uid, pss, 'pass')
        self.assertEqual('Entered password is not valid!', str(_ex.exception))
        # endregion

        # region check succeed scenario
        new_pss = 'NEW pa$$w0rd'
        UserHandler.change_password(user.uid, pss, new_pss)
        u = UserHandler.log_in_by_email(user.email, new_pss)
        self.assertEqual(user.uid, u.uid)
        # endregion

    @staticmethod
    def create_user():
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)
        return user

    def test_retrieve_password_by_email_and_phone(self):
        user = self.create_user()
        # ask for retrieve and
        # save retrieve auth code to db
        result = TokenHandler.generate_token(user.uid, TokenVia.both)
        self.assertTrue(result)

        # get tokens from db
        session = DBInitializer.get_session()
        token = session.query(Token).one()
        session.close()
        # fail scenario: if user does not exist
        with self.assertRaises(SecurityException) as ex:
            UserHandler.change_password_by_hex_token(0, token.hex_token, "New Pa$$w0rd1")
        #       if url token is wrong
        with self.assertRaises(AuthenticationException) as ex:
            UserHandler.change_password_by_url_token("wrong url token", "New Pa$$w0rd1")
        # change password
        new_password = "New Pa$$w0rd"
        result = UserHandler.change_password_by_hex_token(user.uid, token.hex_token, new_password)
        self.assertTrue(result)
        # check if password is really change
        UserHandler.log_in_by_email(user.email, new_password)

        # change password through url token
        result = UserHandler.change_password_by_url_token(token.url_token, "New Pa$$w0rd1")
        self.assertTrue(result)
        # check if password is really change
        UserHandler.log_in_by_email(user.email, "New Pa$$w0rd1")
