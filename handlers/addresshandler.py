from core.exceptions import ValueException
from domain.models import DBInitializer
from domain.models.user import Address, User
from domain.services import address_validation


class AddressHandler:
    _Session = DBInitializer.get_session
    _address_validation = address_validation

    @classmethod
    def add_address(cls, uid, address: Address):
        session = cls._Session()
        user = session.query(User).get(uid)
        if not user:
            raise ValueException(f"there is no user with this id: {uid}")
        cls._address_validation(address)
        user.addresses.append(address)
        session.commit()
        return True

    @classmethod
    def get_address_by_id(cls, uid):
        session = cls._Session()
        return session.query(Address).get(uid)
