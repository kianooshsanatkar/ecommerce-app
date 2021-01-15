from core.exceptions import ValueException
from domain.models import User
from domain.models.user import UserState
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


def get_user_state(user: User):
    if user.first_name and user.last_name and user.phone:
        if user.is_phone_verified:
            if user.email:
                if user.is_email_verified:
                    return UserState.ACTIVE
                return UserState.PARTIALLY
            return UserState.ACTIVE
        return UserState.OBSCURE
    return UserState.INCOMPLETE
