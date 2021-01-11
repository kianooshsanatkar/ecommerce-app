from dataclasses import dataclass
from unittest import TestCase

from core.exceptions import ValueException
from domain.services import address_validation


@dataclass(frozen=True)
class MockAddress:
    province: str
    city: str
    zip_code: str
    postal_address: str
    user_id: int


class AddressValidationTest(TestCase):
    def test_address_raise_value_exception_no_province(self):
        self.assertRaises(ValueException,
                          lambda: address_validation(
                              MockAddress('', 'city', '0123456789', 'postal address', '1')))

    def test_address_raise_value_exception_no_city(self):
        self.assertRaises(ValueException,
                          lambda: address_validation(
                              MockAddress('province', '', '0123456789', 'postal address', 1)))

    def test_address_raise_value_exception_no_zip_code(self):
        self.assertRaises(ValueException,
                          lambda: address_validation(
                              MockAddress('province', 'city', '', 'postal address', 1)))

    def test_address_raise_value_exception_zip_code_length(self):
        self.assertRaises(ValueException,
                          lambda: address_validation(
                              MockAddress('province', 'city', '1' * 9, 'postal address', 1)))
        self.assertRaises(ValueException,
                          lambda: address_validation(
                              MockAddress('province', 'city', '1' * 11, 'postal address', 1)))

    def test_address_raise_value_exception_no_postal_address(self):
        self.assertRaises(ValueException,
                          lambda: address_validation(
                              MockAddress('province', 'city', '0123456789', '', 1)))

    def test_address_raise_value_exception_postal_address_length_maximum(self):
        self.assertRaises(ValueException,
                          lambda: address_validation(
                              MockAddress('province', 'city', '0123456789', 'a' * 512, 1)))

