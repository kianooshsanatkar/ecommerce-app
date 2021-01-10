from core.exceptions import ValueException
from domain.models import User
from domain.services.addressservice import address_validation
from domain.services.contactservice import email_validation, phone_validation
from domain.services.passwordservice import password_validation


def user_validation(user: User):
    if not user.first_name:
        raise ValueException("First Name is Required!")
    if not user.last_name:
        raise ValueException("Last Name is Required!")
    if not user.password:
        raise ValueException("Password is Required!")
    if not password_validation(user.password):
        raise ValueException("Entered password is not valid!")
    if user.email:
        email_validation(user.email)
    if user.phone:
        phone_validation(user.phone)
    if user.addresses:
        for address in user.addresses:
            address_validation(user.address)
    return True




