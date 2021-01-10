from unittest import TestCase

from passlib.hash import pbkdf2_sha256

from core.exceptions import AuthenticationException
from domain.services.passwordservice import password_validation, hashing_password, password_verification, is_it_hashed


class PasswordServiceTest(TestCase):

    def test_password_validation_not_accepted_passwords(self):
        self.assertFalse(password_validation("Tt345"))
        self.assertFalse(password_validation("tt3456"))
        self.assertFalse(password_validation("Tttttt"))
        self.assertFalse(password_validation("123456"))
        self.assertFalse(password_validation("Tt1234'"))
        self.assertFalse(password_validation("Tt1234\""))
        self.assertFalse(password_validation("Tt1234/"))
        self.assertFalse(password_validation("Tt1234\\"))
        self.assertFalse(password_validation("asdf!@#$%"))
        self.assertFalse(password_validation("1234%$#@"))
        self.assertFalse(password_validation("Tt1" * 10 + "32"))
        self.assertFalse(password_validation(""))

    def test_password_validation_accepted_password(self):
        self.assertTrue(password_validation("Tt3456"))
        self.assertTrue(password_validation("123ttT"))
        self.assertTrue(password_validation("As13$#"))
        self.assertTrue(password_validation("AsFd$#"))
        self.assertTrue(password_validation("AFqr1234!@#$%^&*()_+-=[]{}:;<>?"))

    def test_hashing_password(self):
        hashed = hashing_password("password")
        self.assertTrue(pbkdf2_sha256.identify(hashed))

    def test_verification_password_raise_exception(self):
        password = "Pa$$w0rd"
        hashed_pass = pbkdf2_sha256.hash(password)
        with self.assertRaises(AuthenticationException) as _ex:
            password_verification(hashed_pass, "something else")
        self.assertEqual("Entered password is wrong!", str(_ex.exception))

    def test_verification_password_raise_exception_if_entered_password_is_hashed(self):
        password = "Pa$$w0rd"
        hashed_pass1 = pbkdf2_sha256.hash(password)
        hashed_pass2 = pbkdf2_sha256.hash(password)
        with self.assertRaises(AuthenticationException) as _ex:
            self.assertTrue(password_verification(hashed_pass1, hashed_pass2))
        self.assertEqual("Entered Password is hashed!", str(_ex.exception))

    def test_verification_password(self):
        password = "Pa$$w0rd"
        hashed_pass = pbkdf2_sha256.hash(password)
        self.assertTrue(password_verification(hashed_pass, password))

    def test_is_it_hashed_fail(self):
        self.assertFalse(is_it_hashed('not hashed string'))

    def test_is_it_hashed(self):
        hashed = pbkdf2_sha256.hash('random string')
        self.assertTrue(is_it_hashed(hashed))
