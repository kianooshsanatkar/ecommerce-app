from unittest import TestCase

from core.exceptions import ValueException, TypeException
from domain.services import email_validation, phone_validation


class EmailServiceTest(TestCase):

    def test_email_validation_raise_exception_wrong_type(self):
        self.assertRaises(TypeException, lambda: email_validation(1))

    def test_email_validation_wrong_empty_raise_exception(self):
        self.assertRaises(ValueException, lambda: email_validation(''))

    def test_email_validation_raise_exception_wrong_value_extra_space(self):
        # space
        self.assertRaises(ValueException, lambda: email_validation(' simple@domain.tld'))
        # space
        self.assertRaises(ValueException, lambda: email_validation('simple@domain.tld '))
        # space
        self.assertRaises(ValueException, lambda: email_validation('simple @domain.tld'))
        # space
        self.assertRaises(ValueException, lambda: email_validation('simple@ domain.tld'))
        # space
        self.assertRaises(ValueException, lambda: email_validation('simple@domain .tld'))
        # space
        self.assertRaises(ValueException, lambda: email_validation('simple@domain.tld '))
        # space
        self.assertRaises(ValueException, lambda: email_validation('simple@domain. tld'))

    def test_email_validation_raise_exception_too_much_characters(self):
        # too much characters in local name
        self.assertRaises(ValueException, lambda: email_validation(('a' * 65) + '@domain.tld'))
        # too much characters in domain name
        self.assertRaises(ValueException, lambda: email_validation('sample@' + ('a' * 257) + '.tld'))
        # too much characters in tld
        self.assertRaises(ValueException, lambda: email_validation('sample@domain.' + 't' * 65))

    def test_email_validation_value_exception_local_name(self):
        # self.assertRaises(ValueException, lambda: email_validation("1234sample@domain.com"))
        # self.assertRaises(ValueException, lambda: email_validation(".samplesample@domain.com"))
        self.assertRaises(ValueException, lambda: email_validation("_sample@domain.com"))
        self.assertRaises(ValueException, lambda: email_validation(".sample@domain.com"))

    def test_email_validation_valid_emails_local_name(self):
        self.assertTrue(email_validation("sample@domain.com"))
        self.assertTrue(email_validation("sample1234@domain.com"))
        self.assertTrue(email_validation("sample.sample@domain.com"))
        self.assertTrue(email_validation("sample_sample@domain.com"))

    def test_email_validation_valid_emails_domain_name(self):
        self.assertTrue(email_validation("sample@domain.domain.com"))
        self.assertTrue(email_validation("sample@domain-domain.com"))
        self.assertTrue(email_validation("sample@domain.domain.com"))
        self.assertTrue(email_validation("sample@domain1234.com"))

    def test_email_validation_valid_emails_tld(self):
        self.assertTrue(email_validation("sample@domain.com"))
        self.assertTrue(email_validation("sample@domain.com123"))

    def test_email_validation_valid_emails_check_max_length_characters(self):
        # too much characters in local name
        self.assertTrue(email_validation(('a' * 64) + '@domain.tld'))
        # too much characters in domain name
        self.assertTrue(email_validation('sample@' + ('a' * 256) + '.tld'))
        # too much characters in tld
        self.assertTrue(email_validation('sample@domain.' + 't' * 64))


class PhoneServiceTest(TestCase):

    def test_phone_raise_exception_wrong_type(self):
        self.assertRaises(TypeException, lambda: phone_validation(1))

    def test_phone_raise_exception_wrong_phone(self):
        self.assertRaises(ValueException, lambda: phone_validation('1'))
        self.assertRaises(ValueException, lambda: phone_validation('8121234567'))
        self.assertRaises(ValueException, lambda: phone_validation('912123456'))
        self.assertRaises(ValueException, lambda: phone_validation('91212345678'))
        self.assertRaises(ValueException, lambda: phone_validation('9' * 9))
        self.assertRaises(ValueException, lambda: phone_validation('9' * 11))

    def test_phone_success_valid_phone(self):
        self.assertTrue(phone_validation('9121234567'))
        self.assertTrue(phone_validation('9011234567'))
        self.assertTrue(phone_validation('9361234567'))
        self.assertTrue(phone_validation('9' * 10))
