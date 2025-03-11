# ====================================================================
# holder.py
# ====================================================================

from __future__ import annotations

import abc
import sys
import traceback
import warnings
from dataclasses import dataclass

from types import TracebackType
from typing import Any, Generic, Optional, Type, TypeVar, cast, Mapping, Dict

import aiohttp
from aiohttp import ClientResponse

from _HttpClient.utils.compat import json
from _HttpClient.utils.helpers import get_running_loop

# _SessionType = TypeVar("_SessionType", bound=Any)
_SessionType = TypeVar("_SessionType")

_SessionHolderType = TypeVar(
    "_SessionHolderType", bound="AbstractSessionHolder[Any]"
)


# ====================================================================
# ====================================================================
@dataclass
class HTTPResponse:
    """
    Wrapper over different third-party HTTP client responses.
    Оболочка для различных сторонних ответов HTTP-клиентов.
    """

    status_code: int
    body: bytes
    headers: Mapping[str, Any]
    content_type: str  # что-то типа "application/json", "text/html" ...
    _real_response: Any
    #  Оригинальный ответ от стороннего HTTP-клиента.
    #  ... для доступа к дополнительным атрибутам или методам, которые
    #      не включены в обертку.

    # ----------------------------------------------------------------
    # def json(self) -> Any:
    #     return cast(Dict[str, Any], json.loads(self.body))

    # TODO
    def json(self) -> Dict[str, Any]:
        try:
            # Декодируем байты в строку, если это необходимо
            json_str = self.body.decode("utf-8")
            return json.loads(json_str)  # Возвращаем декодированный JSON
        except (json.JSONDecodeError, UnicodeDecodeError) as exception:
            # TODO - можно выбросить исключение или вернуть значение по умолчанию
            raise ValueError("Invalid JSON response") from exception

    # ----------------------------------------------------------------
    def __getattr__(self, item: str) -> Any:
        # метод переопределяет поведение доступа к атрибутам.
        # Если атрибут не найден в экземпляре HTTPResponse,
        # он пытается получить его из _real_response.
        return getattr(self._real_response, item)

    # ----------------------------------------------------------------
    @property
    def has_successful_status_code(self) -> bool:
        # свойство возвращает True, если статусный код меньше 400,
        # и False в противном случае.
        # просто проверяет, что код состояния успешный (т.е. не является
        # ошибкой клиента или сервера).
        return 400 > self.status_code


# ====================================================================
# ====================================================================
class AbstractSessionHolder(abc.ABC, Generic[_SessionType]):
    """
    Управляет жизненным циклом сеанса(ов) и
    позволяет подделывать библиотеку для запросов,
    например, из aiohttp в httpx без каких-либо проблем.
    Holder ленив and allocates in his own state
    session on first call, а не при создании экземпляра.
    """

    # ----------------------------------------------------------------
    def __init__(self, **kwargs: Any) -> None:
        self._session: Optional[_SessionType] = None
        self._session_kwargs = kwargs

    # ----------------------------------------------------------------
    @abc.abstractmethod
    async def convert_third_party_lib_response_to_http_response(
        self, response: Any
    ) -> HTTPResponse:
        raise NotImplementedError

    # ----------------------------------------------------------------
    def update_session_kwargs(self, **kwargs: Any) -> None:
        self._session_kwargs.update(kwargs)

    # ----------------------------------------------------------------
    async def __aenter__(
        self: AbstractSessionHolder[_SessionType],
    ) -> _SessionType:
        self._session = await self.get_session()
        return self._session

    # ----------------------------------------------------------------
    @abc.abstractmethod
    async def get_session(self) -> _SessionType:
        raise NotImplementedError

    # ----------------------------------------------------------------
    async def __aexit__(
        self: AbstractSessionHolder[_SessionType],
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()

    # ----------------------------------------------------------------
    @abc.abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


# ====================================================================
# ====================================================================
class AiohttpSessionHolder(AbstractSessionHolder[aiohttp.ClientSession]):

    _closed = None  # Serves as an uninitialized flag for __del__
    _source_traceback = None  # type: Optional[traceback.StackSummary]

    # ----------------------------------------------------------------
    def __init__(self, **kwargs: Any):

        AbstractSessionHolder.__init__(self, **kwargs)
        self._loop = kwargs.get("loop") or get_running_loop()

        if self._loop.get_debug():
            self._source_traceback = traceback.extract_stack(sys._getframe(1))
        self._closed = False

    # ----------------------------------------------------------------
    def __del__(self, _warnings=warnings):

        if self._closed is False:
            _warnings.warn(
                f"Unclosed AiohttpSessionHolder {self!r}, probably you need to "
                f"close your client after usage or use it as a context manager",
                ResourceWarning,
                source=self,
            )
            context = {
                "session_holder": self,
                "message": f"Unclosed AiohttpSessionHolder {self!r}, probably you need to "
                f"close your client after usage or use it as a context manager",
            }
            if self._source_traceback is not None:
                context["source_traceback"] = self._source_traceback
            self._loop.call_exception_handler(context)

    # ----------------------------------------------------------------
    async def close(self) -> None:

        if self._session_in_working_order():
            await self._session.close()

        self._closed = True

    # ----------------------------------------------------------------
    async def convert_third_party_lib_response_to_http_response(
        self, response: ClientResponse
    ) -> HTTPResponse:

        return HTTPResponse(
            status_code=response.status,
            body=await response.read(),
            headers=response.headers,
            content_type=response.content_type,
            _real_response=response,
        )

    # ----------------------------------------------------------------
    async def get_session(self) -> _SessionType:

        if self._session_in_working_order():
            return self._session
        return await self._instantiate_new_session()

    # ----------------------------------------------------------------
    def _session_in_working_order(self) -> bool:

        return self._session is not None and self._session.closed is False

    # ----------------------------------------------------------------
    async def _instantiate_new_session(self) -> _SessionType:

        self._session: _SessionType = cast(
            _SessionType, aiohttp.ClientSession(**self._session_kwargs)
        )
        return self._session
