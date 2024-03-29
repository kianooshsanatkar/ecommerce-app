class InnerException(BaseException):
    pass


class ValueException(InnerException, ValueError):
    pass


class TypeException(InnerException, TypeError):
    pass


class AuthenticationException(InnerException):
    pass


class AuthorizationException(InnerException):
    pass


class SecurityException(InnerException):
    pass


class TimeoutException(InnerException):
    pass
