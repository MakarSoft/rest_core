# ====================================================================
# base.py
# ====================================================================

import abc

from typing import TypeVar, Generic, Any

from _HttpClient.client.exceptions import MonobankAPIError
from _HttpClient.core.abc.api_method import APIMethod
from _HttpClient.core.session.holder import HTTPResponse

try:
    from orjson import JSONDecodeError as OrjsonDecodeError
except ImportError:
    from json import JSONDecodeError as OrjsonDecodeError

# T = TypeVar("T", bound=Any)
T = TypeVar("T")


class MonobankAPIMethod(APIMethod[T], abc.ABC, Generic[T]):

    @classmethod
    def _validate_response(cls, response: HTTPResponse) -> None:

        if not response.has_successful_status_code:
            raise MonobankAPIError(response)
        elif isinstance(response.json(), list):
            return None
        elif response.json().get("errorDescription") is not None:
            raise MonobankAPIError(response)
