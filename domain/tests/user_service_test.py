from dataclasses import dataclass
from unittest import TestCase

from core.exceptions import ValueException
from domain.services import user_validation


@dataclass(frozen=True)
class TestUser:
    first_name: str
    last_name: str
    phone: str = None
    email: str = None
    addresses: str = None


class UserValidationTest(TestCase):

    def test_user_raise_exception_no_fist_name(self):
        with self.assertRaises(ValueException) as context:
            user_validation(TestUser(first_name='', last_name='last name'))
        self.assertEqual('First Name is Required!', str(context.exception))

    def test_user_raise_exception_no_last_name(self):
        with self.assertRaises(ValueException) as context:
            user_validation(TestUser(first_name='first name', last_name=''))
        self.assertEqual('Last Name is Required!', str(context.exception))

    def test_user_success(self):
        self.assertTrue(user_validation(TestUser(first_name='first name', last_name='last name')))
