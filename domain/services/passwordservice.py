__all__ = ['hashing_password', 'password_verification', 'password_validation', 'is_it_hashed']

import re

from passlib.hash import pbkdf2_sha256 as sha256

from core.exceptions import ValueException, AuthenticationException


def hashing_password(password: str) -> str:
    return sha256.hash(password)


def password_validation(password: str):
    # check if it is hashed with sha256 algorithm
    if is_it_hashed(password):
        raise ValueException('Password already is Hashed!')
    regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[\d\-_\.!@#$%^&*()+=~`:;<>\?,{}[\] ])[a-zA-Z\d\-_\.!@#$%^&*()+=~`:;<>\?," \
            r"{}[\] ]{6,31}$"
    if re.match(regex, password):
        return True
    return False


def password_verification(origin_password, entered_password: str):
    if is_it_hashed(entered_password):
        raise AuthenticationException("Entered Password is hashed!")
    if sha256.verify(entered_password, origin_password):
        return True
    raise AuthenticationException('Entered password is wrong!')


def is_it_hashed(password: str):
    return sha256.identify(password)
