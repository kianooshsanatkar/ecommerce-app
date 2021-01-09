from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import Mock

from core.exceptions import TypeException
from handlers.userhandler import UserHandler


@dataclass(frozen=True)
class MockUser:
    first_name: str = "first name"
    last_name: str = "last name"
    phone: str = None
    email: str = None
    addresses: str = None


class CreateUserHandlerTest(TestCase):

    def setUp(self) -> None:
        self.factory = Mock()
        UserHandler.Session = self.factory.session

    def test_get_user_by_id(self):
        # check if exception rises for the wrong data type
        with self.assertRaises(TypeException) as _ex:
            UserHandler.get_user_by_id('id')
        self.assertEqual("uid parameter type must be int!", str(_ex.exception))
        # check if session and query is called
        UserHandler.get_user_by_id(1)
        self.factory.session.assert_called()
        self.factory.session().query.assert_called()

    def test_get_user_by_email(self):
        # check if exception rises for the wrong data type
        with self.assertRaises(TypeException) as _ex:
            UserHandler.get_user_by_email(1)
        self.assertEqual("email parameter type must be string!", str(_ex.exception))

        # check if email validation is called
        UserHandler.email_validation = self.factory.email_validation
        UserHandler.get_user_by_email('email')
        self.factory.email_validation.assert_called()

        # check if session and query is called
        UserHandler.email_validation = self.factory.email_validation
        UserHandler.get_user_by_email('email')
        self.factory.session.assert_called()
        self.factory.session().query.assert_called()

    def test_create_user_does_validation_called(self):
        UserHandler.user_validation = self.factory.validation
        UserHandler.create_user(Mock())
        self.factory.validation.assert_called()

    def test_create_user_does_add_and_commit_called(self):
        UserHandler.user_validation = self.factory.validation
        UserHandler.create_user(Mock())
        self.factory.session.assert_called()
        self.factory.session().add.assert_called()
        self.factory.session().commit.assert_called()
