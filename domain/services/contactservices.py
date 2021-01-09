import re

from core.exceptions import ValueException, TypeException


def email_validation(email: str) -> bool:
    if not isinstance(email, str):
        raise TypeException(f'Email Type must be string! Type is: {type(email)}')
    if not re.match(r"^[a-zA-Z0-9][\w\d_.]{1,63}@[\w\d\-.]{2,256}\.[\w0-9]{2,64}$", email, re.I):
        raise ValueException(f'Email input is not valid! Email:{email}')
    return True


def phone_validation(phone: str) -> bool:
    if not isinstance(phone, str):
        raise TypeException(f'Phone Type must be string! Type is: {type(phone)}')
    if not re.match(r'^9[0-9]{9}$', phone):
        raise ValueException(f'Input Phone is not valid! phone is:{phone}')
    return True
