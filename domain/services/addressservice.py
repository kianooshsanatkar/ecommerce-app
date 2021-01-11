from core.exceptions import ValueException
from domain.models.user import Address


def address_validation(address: Address):
    if not address.province:
        raise ValueException('province is required!')
    if not address.city:
        raise ValueException('city is required!')
    if not address.zip_code or len(address.zip_code) != 10:
        raise ValueException('zip code is required!')
    if not address.postal_address or len(address.postal_address) >= 512:
        raise ValueException('postal address is required!')
