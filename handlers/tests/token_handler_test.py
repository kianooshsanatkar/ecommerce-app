from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import Mock

from core.exceptions import SecurityException, InnerException, TimeoutException
from domain.models import Token
from domain.models.token import ExchangeMethods
from handlers.tokenhandler import TokenHandler


class TokenHandlerTest(TestCase):

    # def setUp(self) -> None:

    def test_generate_new_token_error_wrong_user_id(self):
        TokenHandler._Session = Mock()
        TokenHandler._get_user = Mock(return_value=None)
        # print(TokenHandler.generate_token(0, TokenVia.phone_number))
        with self.assertRaises(SecurityException) as ex:
            TokenHandler.generate_token(0, ExchangeMethods.PHONE)
        self.assertTrue("User doesn't exist!" in str(ex.exception))

    def test_generate_new_token_check_if_data_provided(self):
        TokenHandler._Session = Mock()
        TokenHandler._get_user = Mock()

        def pr(token):
            self.assertIsNotNone(token.hex_token)
            self.assertIsNotNone(token.url_token)
            self.assertIsNotNone(token.url_token)
            self.assertTrue(token.requested_time < datetime.utcnow())

        TokenHandler._Session().add = pr
        TokenHandler.generate_token(0, ExchangeMethods.EMAIL)
        TokenHandler._Session().commit.assert_called()

    def test_generate_new_token_error_deactivated_token(self):
        TokenHandler._Session = Mock()
        TokenHandler._get_user = Mock()
        TokenHandler._Session().query().filter_by().order_by().first = Mock(
            return_value=Token(deactivate=False, time_limit=datetime.utcnow() - timedelta(minutes=-10),
                               exchange_method=ExchangeMethods.PHONE.value))
        with self.assertRaises(InnerException) as ex:
            TokenHandler.generate_token(0, ExchangeMethods.PHONE)
        self.assertEqual("A valid token already issued!", str(ex.exception))

    def test_hexadecimal_token_validation_error_deactivated_token(self):
        TokenHandler._Session = Mock()
        TokenHandler._Session().query().filter_by().order_by().first = Mock(return_value=Token(deactivate=True))
        with self.assertRaises(SecurityException) as ex:
            TokenHandler.hexadecimal_token_validation(1, 'token')
        self.assertEqual('Token is Deactivated!', str(ex.exception))

    def test_hexadecimal_token_validation_error_expired_token(self):
        TokenHandler._Session = Mock()
        TokenHandler._Session().query().filter_by().order_by().first = Mock(
            return_value=Token(deactivate=False, time_limit=(datetime.utcnow()) - timedelta(minutes=2)))
        with self.assertRaises(TimeoutException) as ex:
            TokenHandler.hexadecimal_token_validation(1, 'token')
        self.assertEqual('Token is Expired!', str(ex.exception))
