from unittest import TestCase

from sqlalchemy.orm import close_all_sessions

from core.exceptions import ValueException
from domain.models import User, DBInitializer
from domain.models import db_Base
from domain.models.user import Address
from handlers import UserHandler
from handlers.addresshandler import AddressHandler
from integration_tests.helper import reset_user_handler_injection


class AddressTest(TestCase):
    @staticmethod
    def setUpClass():
        reset_user_handler_injection()

    def setUp(self) -> None:
        db_Base.metadata.create_all(bind=DBInitializer.get_engine())

    def tearDown(self) -> None:
        close_all_sessions()
        db_Base.metadata.drop_all(bind=DBInitializer.get_new_engine())

    def test_add_address_to_user_addresses(self):
        user = User(password='Pa$$w0rd', first_name='first name', last_name='last name', phone='9121234567',
                    email='email@domain.tld')
        UserHandler.create_user(user)

        # region Succeed Scenario
        address = Address(province='tehran', city='tehran', zip_code='1' * 10,
                          postal_address='somewhere in tehran')
        result = AddressHandler.add_address(user.uid, address)
        self.assertTrue(result)
        add = AddressHandler.get_address_by_id(address.uid)
        self.assertEqual(address.province, add.province)
        self.assertEqual(address.city, add.city)
        self.assertEqual(address.zip_code, add.zip_code)
        self.assertEqual(address.postal_address, add.postal_address)
        # endregion

        # region Failed Scenario
        new_address = Address(city='tehran', zip_code='1' * 10,
                              postal_address='somewhere in tehran')
        with self.assertRaises(ValueException):
            AddressHandler.add_address(user.uid, new_address)

        new_address = Address(province='tehran', zip_code='1' * 10,
                              postal_address='somewhere in tehran')
        with self.assertRaises(ValueException):
            AddressHandler.add_address(user.uid, new_address)

        new_address = Address(province='tehran', city='tehran', zip_code='0123456789')
        with self.assertRaises(ValueException):
            AddressHandler.add_address(user.uid, new_address)

        new_address = Address(province='tehran', city='tehran', postal_address='somewhere in tehran')
        with self.assertRaises(ValueException) as _ex:
            AddressHandler.add_address(12345, new_address)
        self.assertEqual("there is no user with this id: 12345", str(_ex.exception))
        # endregion
