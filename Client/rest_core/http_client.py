# ====================================================================
# http_client.py
# ====================================================================

from __future__ import annotations

import asyncio
import aiohttp
from aiohttp import client_exceptions
import yarl
import json as j

from dataclasses import dataclass

from async_timeout import timeout

from collections.abc import Iterable

from pydantic import BaseModel, ValidationError

from typing import (
    Optional,
    Union,
    Type,
    TypeVar,
    Mapping,
    # , TracebackType  # 3.10
    # , Self   # 3.11
)

from project.logger.logger_config import get_logger_config

# import project.schemas
from project.schemas import Response, BaseResponse, DataType

from project.rest_core.auth import Auth
from project.rest_core.http_codes import HTTP_Codes
from project.rest_core.http_headers import HttpHeaders

from project.rest_core.session import Session, TOTAL_TIMEOUT

from project.rest_core.token import Token
from project.rest_core.exceptions import (
    HttpClientTimeotError,
    HttpClientConnectionError,
    HttpClientResponseError,
    JsonFormatError,
    ApiInternalError,
    DataValidationError,
    DataFormatError,
)

P = TypeVar("P", bound=BaseModel)
T = Union[P, list[P]]

logger = get_logger_config()


# ==============================================================================
# ContentType
# ==============================================================================
@dataclass
class ContentType:
    """ """

    main_type: Optional[str]
    sub_types: Optional[tuple[str, str]]
    params: Optional[dict[str, str]]


# ====================================================================
# HTTPClient
# ====================================================================
class HTTPClient:
    """ """

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __init__(
        self,
        session: Session,
        url: str,
        *,
        auth: Optional[Auth] = None,
        headers: Optional[HttpHeaders] = None,
        payload: Optional[Mapping[str, Union[str, int, float]]] = None,
    ) -> None:

        self.url = url
        self.session = session
        self.auth = auth
        self.headers = headers or HttpHeaders()
        self.payload = payload

        self.token: Optional[Token] = None

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    @property
    def token(self) -> Optional[Token]:
        return self._token

    @token.setter
    def token(self, token: Optional[Token]) -> None:
        self._token = None
        if isinstance(token, Token) and token.is_valid():
            self._token = token

    # ----------------------------------------------------------------
    # clear_auth_head
    # ----------------------------------------------------------------
    def clear_auth_head(self) -> None:
        if isinstance(self.headers, HttpHeaders):
            self.headers.del_headers_item("Authorization")

    # ----------------------------------------------------------------
    # get_auth_head
    # ----------------------------------------------------------------
    def get_auth_head(self) -> Optional[str]:
        str_token: Optional[str] = None
        if isinstance(self.headers, HttpHeaders):
            str_token = self.headers.get_header_value("Authorization-Type")
        return str_token

    # ----------------------------------------------------------------
    # set_auth_head
    # ----------------------------------------------------------------
    def set_auth_head(self) -> None:
        if isinstance(self.headers, HttpHeaders):
            if self.token:
                # сохраняем строковое представление токена...
                self.headers.set_header_value(
                    "Authorization", self.token.token
                )
            else:
                self.clear_auth_head()

    # ----------------------------------------------------------------
    # get_content_type
    # ----------------------------------------------------------------
    def get_content_type(self, res: aiohttp.ClientResponse) -> ContentType:

        main_type = sub_types = params = None

        if res:
            header_content_type: Optional[str] = res.headers.get(
                "Content-Type"
            )
            if header_content_type:
                items = header_content_type.split(";")

                # анализируем первый элемент
                main_type, sub_type = map(str.lower, items[0].split("/", 1))
                sub_types = (
                    sub_type.split("+", 1)
                    if "+" in sub_type
                    else (sub_type, "")
                )

                # обрабатываем дополнительные параметры...
                params = dict(
                    item.split("=", 1) if "=" in item else (item, "")
                    for item in items[1:]
                )

        return ContentType(main_type, sub_types, params)

    # ----------------------------------------------------------------
    # make_request
    # ----------------------------------------------------------------
    async def make_request(
        self,
        method: str,
        url_part: str,
        *,
        auth: Optional[aiohttp.BasicAuth] = None,
        headers: Optional[HttpHeaders] = None,
        params: Optional[Mapping[str, str]] = None,
        payload: Optional[Mapping[str, Union[str, int, float]]] = None,
        auth_required: bool = False,
        request_timeout: Optional[float] = None,
        response_model: P = None,
    ) -> Optional[Response]:
        """ """

        headers = headers or self.headers or HttpHeaders()
        payload = payload or self.payload
        params = params or None
        # if not headers:
        #     headers = self.headers or HttpHeaders()

        # if not payload:
        #     # payload = self.payload if self.payload else {}
        #     payload = self.payload

        # if not params:
        #     # params = {}
        #     params = None

        if auth_required:
            # требуется токен для авторизации ...
            if self.token and self.token.is_valid():
                self.set_auth_head()
            else:
                logger.error("=== нет авторизационных данных  ===\n")
                # print('нет авторизационных данных')
                return None

        # Авторизационная информация указанная в заголовке имеет приоритет
        if "Authorization" in headers.headers:
            auth = None
        else:
            # при отсутствии авторизационной информации в заголовке -
            # формируем авторизационную информацию на основании переданных
            # или сохраненных данных...
            if not auth:
                auth = self.auth

        if self.url and url_part:
            url = f"{self.url}/{url_part}"
        else:
            url = self.url or url_part
        if not url:
            # raise ActionURLMatchError('Невозможно сформировать URL для запрос')
            logger.error(f"=== URL Match Error  {self.url}; {url_part} ===\n")
            # print('Невозможно сформировать URL для запрос')
            return None

        if not request_timeout:
            if self.session.timeout.total:
                request_timeout = self.session.timeout.total
            else:
                request_timeout = TOTAL_TIMEOUT

        # все данные собраны - пытаемся выполнить запрос
        try:
            with timeout(request_timeout):
                # url, #yarl.URL(url, encoded=True),
                res = await self.session._request(
                    method,
                    url,
                    auth=auth,
                    json=payload,
                    params=params,
                    headers=headers.headers,
                    verify_ssl=False,
                )

        # ---start [обработка ошибок]---
        except asyncio.TimeoutError as exception:
            # таймаут
            # logger.error(
            #     f'=== Client timeout occured with connecting to  {url} ==='
            # )
            raise HttpClientTimeotError(
                f"Timeout occured with connecting to {url}"
            ) from exception

        # ------------------------------
        except (
            client_exceptions.ClientConnectionError,
            client_exceptions.ClientConnectorError,
        ) as exception:
            # низкоуровневые проблемы подключения...
            # logger.error(
            #     f'=== Client connection error, to {url} ==='
            # )
            raise HttpClientConnectionError(
                f"Client connection error, to {url}"
            ) from exception

        # ------------------------------
        except client_exceptions.ClientResponseError as exception:
            # исключение возникшее после получения ответа от сервера
            # logger.error(
            #     f'=== Client response error from {url} ==='
            # )
            raise HttpClientResponseError(
                f"Client response error from {url}"
            ) from exception

        # ------------------------------
        except Exception as exception:
            # прочая фигня....
            # logger.error(
            #     f'=== Client ERROR from {url} ==='
            # )
            raise ApiInternalError(f"Ошибка в приложении") from exception

        # --- end [обработка ошибок] ---

        else:
            # if (res.status // 100 ) in (4,5):
            #     res.close()

            # content_type = self.get_content_type(res)
            # if content_type.main_type == 'application' and any('json' in st for st in content_type.sub_types):
            #     print('+'.join(content_type.sub_types))

            # Обработка полученных данных
            text = await res.text()
            if text:
                try:

                    # предполагаем json-контент => десериализуем строковое представление в dict
                    data = deserialized_data = j.loads(text)
                    # data = deserialized_data = await res.json()

                except Exception as exception:
                    # не json => сохраняем только строковое представление
                    data = text
                    # raise JsonFormatError("Not JSON data format") from exception

                if not response_model:
                    response_model = Response[DataType]

                try:

                    response = response_model(
                        status_code=res.status, headers=res.headers, data=data
                    )

                except ValidationError as exception:
                    # данные не соответствуют модели
                    raise DataValidationError(
                        "Data Validation Error"
                    ) from exception

                except Exception as exception:
                    # Общая ошибка - не должно быть...
                    raise DataFormatError("Data Format Error") from exception

            return response

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    async def get(
        self,
        url_part: str,
        *,
        response_model: Type[Union[list[BaseModel], BaseModel]],
        auth: Optional[aiohttp.BasicAuth] = None,
        payload: Optional[dict[str, Union[str, int]]] = None,
        params: Optional[dict[str, str]] = None,
        auth_required: bool = False,
    ) -> Response:
        """"""

        try:
            ret = await self.make_request(
                method="GET",
                url_part=url_part,
                auth=auth,
                payload=payload,
                params=params,
                auth_required=auth_required,
                response_model=response_model,
            )
        except Exception as exception:
            logger.error(f"=== Client get ===\n   details:\n{exception}\n\n")
            raise (exception)

        return ret

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    async def post(
        self,
        url_part: str,
        *,
        response_model: Type[Union[list[BaseModel], BaseModel]],
        auth: Optional[aiohttp.BasicAuth] = None,
        payload: Optional[dict[str, Union[str, int]]] = None,
        params: Optional[dict[str, str]] = None,
        auth_required: bool = False,
    ) -> Response:
        """"""
        try:
            ret = await self.make_request(
                method="POST",
                url_part=url_part,
                auth=auth,
                payload=payload,
                params=params,
                auth_required=auth_required,
                response_model=response_model,
            )
        except Exception as exception:
            logger.error(f"=== Client post ===\n   details:\n{exception}\n\n")
            raise (exception)
        return ret

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    async def close_session(self):
        """ """

        await self.session.close()

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    async def __aenter__(self) -> HTTPClient:
        """ """

        return self

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """ """

        # await self.close_session()
        pass

    # ----------------------------------------------------------------
    # async def __aexit__(
    #     self,
    #     exc_type: Optional[Type[BaseException]],
    #     exc_val: Optional[BaseException],
    #     exc_tb
    # ) -> Optional[bool]:
    #     ''''''
    #     await self.close()
    #     return None

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __str__(self) -> str:
        """ """

        return f"{self.__class__.__name__}<token={self._api_token}>"
