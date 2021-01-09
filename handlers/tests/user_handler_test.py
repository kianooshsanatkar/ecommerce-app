from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import Mock

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
