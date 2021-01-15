import secrets
from datetime import datetime

from sqlalchemy import desc

from core.exceptions import SecurityException, TimeoutException, AuthenticationException, InnerException
from domain.models import DBInitializer
from domain.models import Token
from domain.models.token import ExchangeMethods


def get_user_builder(user_id):
    from handlers import UserHandler
    return UserHandler.get_user_by_id(user_id)


class TokenHandler:
    _Session = DBInitializer.get_session
    _get_user = get_user_builder

    @classmethod
    def generate_token(cls, user_id: int, via: ExchangeMethods) -> bool:
        u = cls._get_user(user_id)
        if not u:
            raise SecurityException(f"User doesn't exist! user_id: {user_id}")
        if via == ExchangeMethods.PHONE and not u.phone:
            raise InnerException('User phone is not registered')
        if via == ExchangeMethods.EMAIL and not u.email:
            raise InnerException('User email is not registered')
        session = cls._Session()

        last_token = session.query(Token).filter_by(user_id=user_id).order_by(desc(Token.requested_time)).first()

        if last_token and not last_token.deactivate and last_token.exchange_method == via.value \
                and datetime.utcnow() < last_token.time_limit:
            raise InnerException('A valid token already issued!')
        token = Token(user_id=u.uid, requested_time=datetime.utcnow())
        token.hex_token = secrets.token_hex(2)
        token.url_token = secrets.token_urlsafe()
        token.exchange_method = via.value
        session.add(token)
        session.commit()
        # Todo: ******* send the token to the service provider (MailService|SMSService) ********
        return True

    @classmethod
    def hexadecimal_token_validation(cls, user_id, auth_token: str, exchange_method: ExchangeMethods = None) -> bool:
        session = cls._Session()
        token = None
        if exchange_method:
            token = session.query(Token).filter_by(user_id=user_id, exchange_method=exchange_method.value).order_by(
                desc(Token.requested_time)).first()
        else:
            token = session.query(Token).filter_by(user_id=user_id).order_by(desc(Token.requested_time)).first()
        if not token:
            raise SecurityException('User has no token!')
        if token.deactivate:
            raise SecurityException('Token is Deactivated!')
        if datetime.utcnow() > token.time_limit:
            raise TimeoutException('Token is Expired!')
        if secrets.compare_digest(token.hex_token, auth_token):
            token.last_used_time = datetime.utcnow()
            session.commit()
            return token.exchange_method
        token.failed_attempts += 1
        if token.failed_attempts > 3:
            token.deactivate = True
        session.commit()
        if token.deactivate:
            raise SecurityException('Token is Deactivated!')
        raise AuthenticationException('Token is not valid!')

    @classmethod
    def url_token_validation(cls, url_token: str) -> ():
        session = cls._Session()
        tk = session.query(Token).filter_by(url_token=url_token).first()
        if not tk:
            raise AuthenticationException('Url Token is not valid!')
        if tk.deactivate:
            raise SecurityException('Token is Deactivated!')
        if datetime.utcnow() > tk.time_limit:
            raise TimeoutException('Token is Expired!')
        tk.last_used_time = datetime.utcnow()
        return tk.user.uid, tk.exchange_method
