from dataclasses import dataclass
from datetime import datetime
from unittest import TestCase

from core.exceptions import ValueException
from domain.models.user import UserState
from domain.services import user_validation
from domain.services.userservices import get_user_state


@dataclass(frozen=True)
class MockUser:
    first_name: str = 'first name'
    last_name: str = 'last name'
    password: str = 'Pa$$w0rd'
    phone: str = None
    email: str = None
    birth: datetime = None
    addresses: str = None
    is_email_verified: bool = False
    is_phone_verified: bool = False


class UserValidationTest(TestCase):

    def test_user_raise_exception_no_fist_name(self):
        with self.assertRaises(ValueException) as context:
            user_validation(MockUser(first_name='', last_name='last name'))
        self.assertEqual('First Name is Required!', str(context.exception))

    def test_user_raise_exception_no_last_name(self):
        with self.assertRaises(ValueException) as context:
            user_validation(MockUser(first_name='first name', last_name=''))
        self.assertEqual('Last Name is Required!', str(context.exception))

    def test_user_success(self):
        self.assertTrue(user_validation(MockUser(first_name='first name', last_name='last name')))

    def test_user_no_password_raise_exception(self):
        with self.assertRaises(ValueException) as _ex:
            user_validation(MockUser(password=''))

    def test_user_raise_password_validation_exception(self):
        with self.assertRaises(ValueException) as _ex:
            user_validation(MockUser(password="password"))
        self.assertEqual("Entered password is not valid!", str(_ex.exception))

    def test_user_valid_password_validation(self):
        self.assertTrue(user_validation(MockUser(password="Pa$$w0rd")))

    # region User State Tests

    def test_get_user_state_incomplete(self):
        user = MockUser(first_name="first_name", last_name="", password="", phone="", email="")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="", last_name="last name", password="", phone="", email="")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="", last_name="", password="password", phone="", email="")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="", last_name="", password="", phone="phone", email="")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="", last_name="", password="", phone="", email="email")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="first name", last_name="last name", password="", phone="", email="")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="", last_name="", password="", phone="phone", email="email")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="first name", last_name="last name", password="", phone="", email="email")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))
        user = MockUser(first_name="", last_name="last name", password="", phone="1234", email="1324")
        self.assertEqual(UserState.INCOMPLETE, get_user_state(user))

    def test_get_user_state_obscure(self):
        user = MockUser(first_name="first_name", last_name="last_name", phone="1234", email="email")
        self.assertEqual(UserState.OBSCURE, get_user_state(user))
        user = MockUser(first_name="first_name", last_name="last_name", phone="1234", email="email",
                        is_phone_verified=False, is_email_verified=True)
        self.assertEqual(UserState.OBSCURE, get_user_state(user))

    def test_get_user_state_partially(self):
        user = MockUser(first_name="first_name", last_name="last_name", phone="1234", email="email",
                        is_phone_verified=True, is_email_verified=False)
        self.assertEqual(UserState.PARTIALLY, get_user_state(user))

    def test_get_user_state_active(self):
        user = MockUser(first_name="first_name", last_name="last_name", phone="1234", email="email",
                        is_phone_verified=True, is_email_verified=True)
        self.assertEqual(UserState.ACTIVE, get_user_state(user))
        user = MockUser(first_name="first_name", last_name="last_name", phone="1234", email=None,
                        is_phone_verified=True, is_email_verified=False)
        self.assertEqual(UserState.ACTIVE, get_user_state(user))
    # endregion
