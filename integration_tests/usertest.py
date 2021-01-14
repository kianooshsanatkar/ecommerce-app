from dataclasses import dataclass
from datetime import datetime
from unittest import TestCase

from sqlalchemy.orm import close_all_sessions

from core.exceptions import AuthenticationException, ValueException, SecurityException
from domain.models import User, Token
from domain.models import db_Base as Base, DBInitializer
from handlers import UserHandler
from handlers.tokenhandler import TokenHandler, TokenVia
from integration_tests.helper import reset_user_handler_injection, reset_token_handler_injection


@dataclass
class UserDTO:
    first_name: str = 'first name'
    last_name: str = 'last name'
    email: str = 'email@domain.tld'
    phone: str = '9121234567'


class UserTest(TestCase):

    @staticmethod
    def setUpClass():
        reset_user_handler_injection()
        reset_token_handler_injection()

    def setUp(self) -> None:
        Base.metadata.create_all(bind=DBInitializer.get_engine())

    def tearDown(self) -> None:
        close_all_sessions()
        Base.metadata.drop_all(bind=DBInitializer.get_new_engine())

    def test_create_and_get_user(self):
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld', birth=datetime(1988, 1, 1).date())
        uid = UserHandler.create_user(user)
        u = UserHandler.get_user_by_id(uid)
        # assert user properties with origin properties
        self.assertEqual(user.first_name, u.first_name)
        self.assertEqual(user.last_name, u.last_name)
        self.assertEqual(user.phone, u.phone)
        self.assertEqual(user.email, u.email)
        self.assertEqual(user.birth, u.birth)
        # check if password is null
        self.assertIsNone(u.password)

    # this test can be deleted at anytime, this is a self experience, not related to any business of the application
    def test_db_check_if_different_session_affect_entities(self):
        session = DBInitializer.get_session()
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld', birth=datetime(1988, 1, 1).date())
        uid = UserHandler.create_user(user)
        u = UserHandler.get_user_by_id(uid)
        u.first_name = 'New_Name'
        session.commit()
        n_u = UserHandler.get_user_by_id(uid)
        self.assertNotEqual(n_u.first_name, 'New_Name')
        uu = session.query(User).get(u.uid)
        self.assertIsNotNone(uu.password)

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
