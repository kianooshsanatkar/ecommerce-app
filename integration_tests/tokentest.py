from datetime import datetime, timedelta
from unittest import TestCase

from sqlalchemy.orm import close_all_sessions

from core.exceptions import AuthenticationException, SecurityException, TimeoutException, InnerException
from domain.models import DBInitializer, User, Token
from domain.models import db_Base as Base
from domain.models.token import TIME_SPAN, ExchangeMethods
from domain.services import user_validation, email_validation, passwordservice
from handlers import UserHandler
from handlers.tokenhandler import TokenHandler


class TokenTest(TestCase):

    def setUpClass() -> None:
        # reset all UserHandler dependencies
        UserHandler._Session = DBInitializer.get_session
        UserHandler._user_validation = user_validation
        UserHandler._email_validation = email_validation
        UserHandler._hashing = passwordservice.hashing_password
        UserHandler._password_service = passwordservice

        # reset all token dependencies
        TokenHandler._Session = DBInitializer.get_session
        TokenHandler._get_user = UserHandler.get_user_by_id

    def setUp(self) -> None:
        Base.metadata.create_all(bind=DBInitializer.get_engine())

    def tearDown(self) -> None:
        close_all_sessions()
        Base.metadata.drop_all(bind=DBInitializer.get_new_engine())

    @staticmethod
    def create_user(just_phone: bool=False):
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        if just_phone:
            user.email = None
        user_id = UserHandler.create_user(user)
        return user_id

    def generate_toke(self, no_exchange=False, user_id=None):
        if user_id is None:
            if no_exchange:
                user_id = UserHandler.create_user(
                    User(password='Pa$$w0rd', first_name='first name', last_name='last name'))
            else:
                user_id = self.create_user()
        result = TokenHandler.generate_token(user_id, ExchangeMethods.PHONE)
        return user_id, result

    def test_generate_token(self):
        self.create_user()
        # get token
        session = TokenHandler._Session()
        self.assertEqual(2, session.query(Token).count())
        token = session.query(Token).first()
        # check the approximate requested_time
        self.assertTrue(datetime.utcnow() > token.requested_time > datetime.utcnow() - timedelta(minutes=1))
        self.assertTrue(token.time_limit > datetime.utcnow())
        # check the approximate time_limit
        time_limit = token.requested_time + TIME_SPAN
        self.assertTrue(time_limit - timedelta(minutes=1) < token.time_limit < time_limit + timedelta(minutes=1))
        self.assertIsNotNone(token.hex_token)
        self.assertTrue(len(token.hex_token) == 4)
        self.assertIsNotNone(token.url_token)
        self.assertTrue(len(token.url_token) == 43)
        self.assertEqual(token.failed_attempts, 0)
        self.assertEqual(token.deactivate, False)
        self.assertIsNone(token.last_used_time)

    def test_generate_token_raise_if_already_valid_token_available(self):
        user_id = self.create_user()
        with self.assertRaises(InnerException) as ex:
            self.generate_toke(user_id=user_id)
        self.assertEqual('A valid token already issued!', str(ex.exception))

    def test_verification_token(self):
        user_id = self.create_user()
        session = DBInitializer.get_session()
        # for Phone
        token = session.query(Token).filter_by(exchange_method=ExchangeMethods.PHONE.value).first()

        self.assertIsNone(token.last_used_time)
        tk_ex_method = TokenHandler.hexadecimal_token_validation(user_id, token.hex_token, ExchangeMethods.PHONE)
        self.assertIsNotNone(tk_ex_method)
        self.assertEqual(ExchangeMethods.PHONE.value, tk_ex_method)
        session.refresh(token)
        self.assertIsNotNone(token.last_used_time)
        self.assertTrue(datetime.utcnow() > token.last_used_time > datetime.utcnow() - timedelta(minutes=1))
        tk_user_id, ex_method = TokenHandler.url_token_validation(token.url_token)
        self.assertEqual(user_id, tk_user_id)
        self.assertEqual(ExchangeMethods.PHONE.value, ex_method)
        self.assertTrue(datetime.utcnow() > token.last_used_time > datetime.utcnow() - timedelta(minutes=1))

        # for EMAIL
        token = session.query(Token).filter_by(exchange_method=ExchangeMethods.EMAIL.value).first()
        self.assertIsNone(token.last_used_time)
        tk_ex_method = TokenHandler.hexadecimal_token_validation(user_id, token.hex_token, ExchangeMethods.EMAIL)
        self.assertIsNotNone(tk_ex_method)
        self.assertEqual(ExchangeMethods.EMAIL.value, tk_ex_method)
        session.refresh(token)
        self.assertIsNotNone(token.last_used_time)
        self.assertTrue(datetime.utcnow() > token.last_used_time > datetime.utcnow() - timedelta(minutes=1))
        tk_user_id, ex_method = TokenHandler.url_token_validation(token.url_token)
        self.assertEqual(user_id, tk_user_id)
        self.assertEqual(ExchangeMethods.EMAIL.value, ex_method)
        self.assertTrue(datetime.utcnow() > token.last_used_time > datetime.utcnow() - timedelta(minutes=1))

    def test_verification_token_error_if_user_id_is_wrong(self):
        user_id = self.create_user()
        # empty database
        with self.assertRaises(SecurityException) as ex:
            TokenHandler.hexadecimal_token_validation(0, "some wrong Token")
        self.assertEqual('User has no token!', str(ex.exception))
        # wrong user_id
        with self.assertRaises(SecurityException) as ex:
            TokenHandler.hexadecimal_token_validation(0, "some wrong Token")
        self.assertEqual('User has no token!', str(ex.exception))

    def test_verification_token_error_wrong_token_and_deactivated_token(self):
        user_id = self.create_user(just_phone=True)

        with self.assertRaises(AuthenticationException) as ex:
            TokenHandler.url_token_validation("some wrong Token")
        self.assertEqual('Url Token is not valid!', str(ex.exception))

        # failed 3 times
        for i in range(3):
            with self.assertRaises(AuthenticationException) as ex:
                TokenHandler.hexadecimal_token_validation(user_id, 'wrong token')
            self.assertEqual("Token is not valid!", str(ex.exception))

        for i in range(2):
            with self.assertRaises(SecurityException) as ex:
                TokenHandler.hexadecimal_token_validation(user_id, 'wrong token')
            self.assertEqual('Token is Deactivated!', str(ex.exception))

        # check deactivated token raise exception even for right Hex token
        session = DBInitializer.get_session()
        token = session.query(Token).one()
        with self.assertRaises(SecurityException) as ex:
            TokenHandler.hexadecimal_token_validation(user_id, token.hex_token)
        self.assertEqual('Token is Deactivated!', str(ex.exception))

        # check deactivated token raise exception even for right URL token
        with self.assertRaises(SecurityException) as ex:
            TokenHandler.url_token_validation(token.url_token)
        self.assertEqual('Token is Deactivated!', str(ex.exception))

    def test_verification_token_error_expired_token(self):
        # generate a token
        user_id = self.create_user(just_phone=True)

        # update it's database session with expired token
        session = DBInitializer.get_session()
        token = session.query(Token).one()
        token.time_limit = datetime.utcnow() - timedelta(minutes=1)
        session.commit()

        # check if raise expires
        with self.assertRaises(TimeoutException):
            TokenHandler.hexadecimal_token_validation(user_id, token.hex_token)
        with self.assertRaises(TimeoutException):
            TokenHandler.url_token_validation(token.url_token)

        result = self.generate_toke(user_id=user_id)
        self.assertTrue(result)
