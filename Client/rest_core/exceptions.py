# ====================================================================
# exceptions.py
#
# ====================================================================

from typing import Any


# --------------------------------------------------------------------
# --- исключения http_client
class HttpClientTimeotError(Exception):
    pass


class HttpClientConnectionError(Exception):
    pass


class HttpClientResponseError(Exception):
    pass


class JsonFormatError(Exception):
    pass


class DataValidationError(Exception):
    pass


class DataFormatError(Exception):
    pass


# --------------------------------------------------------------------
# --- исключения уровня REST-API
class ApiInternalError(Exception):
    pass


class ApiUrlError(Exception):
    pass


class ApiResourceNotFound(Exception):
    pass


class ApiContentTypeError(Exception):
    pass


class ApiResponseValidationError(Exception):
    pass


class ResourceNotAppendToApi(Exception):
    pass


class ActionNotFound(Exception):
    pass


class ActionURLMatchError(Exception):
    pass


class ApiAuthFormatError(Exception):
    pass


class ApiPasswordFormatError(Exception):
    pass


class ApiEncodingFormatError(Exception):
    pass


class ApiActionNotFound(Exception):
    pass


# --------------------------------------------------------------------


class ErrorWithResponse(Exception):
    def __init__(self, message: str, response: Any = None) -> None:
        self.message = message
        self.response = response


class ServerError(ErrorWithResponse):
    pass


class ClientError(ErrorWithResponse):
    pass


class AuthError(ClientError):
    pass


class NotFoundError(ClientError):
    pass
