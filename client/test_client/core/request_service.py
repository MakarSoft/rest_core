# ====================================================================
# request_service.py
# ====================================================================

import logging

from dataclasses import dataclass
from typing import Any, Dict, Optional, TypeVar

from aiohttp.typedefs import LooseCookies

from _HttpClient.core.abc.api_method import APIMethod

from _HttpClient.core.session.holder import (
    AbstractSessionHolder,
    AiohttpSessionHolder,
    HTTPResponse,
)

from _HttpClient.utils.compat import Protocol
from _HttpClient.utils.payload import make_payload

logger = logging.getLogger("aiomonobank.RequestService")

T = TypeVar("T")


@dataclass
class RequestParams:
    """
    структура для хранения параметров запроса.
    """

    url: str
    method: str
    cookies: Optional[LooseCookies] = None
    json: Optional[Any] = None
    data: Optional[Any] = None
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    kwargs: Optional[Dict[str, Any]] = None


class RequestServiceProto(Protocol):

    async def execute_api_method(
        self, method: APIMethod[T], **url_kw: Any
    ) -> T:

        try:
            request = method.build_request(**url_kw)
            raw_http_response = await self.send_request(
                request.endpoint,
                request.http_method,
                params=request.params,
                data=request.data,
                headers=request.headers,
                json=request.json_payload,
            )
            return method.parse_http_response(raw_http_response)
        except Exception as e:
            logger.error(f"Error executing API method: {e}")
            raise

    # async def execute_api_method(
    #     self, method: APIMethod[T], **url_kw: Any
    # ) -> T: ...

    async def get_json_content(
        self,
        url: str,
        method: str,
        cookies: Optional[LooseCookies] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Any] = None,
        params: Optional[Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]: ...

    async def send_request(
        self, request_params: RequestParams
    ) -> HTTPResponse:
        try:
            session = await self._session_holder.get_session()
            return await self._session_holder.convert_third_party_lib_response_to_http_response(
                await session.request(
                    method=request_params.method,
                    url=request_params.url,
                    data=request_params.data,
                    headers=request_params.headers,
                    json=request_params.json,
                    cookies=request_params.cookies,
                    params=request_params.params,
                    **request_params.kwargs,
                )
            )
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            raise

    # async def send_request(
    #     self,
    #     url: str,
    #     method: str,
    #     cookies: Optional[LooseCookies] = None,
    #     json: Optional[Any] = None,
    #     data: Optional[Any] = None,
    #     headers: Optional[Any] = None,
    #     params: Optional[Any] = None,
    #     **kwargs: Any,
    # ) -> HTTPResponse: ...

    async def warmup(self) -> Any: ...

    async def shutdown(self) -> None: ...


class RequestService:

    def __init__(
        self,
        session_holder: Optional[AbstractSessionHolder[Any]] = None,
    ) -> None:
        if session_holder is None:
            session_holder = AiohttpSessionHolder()
        self._session_holder = session_holder

    async def execute_api_method(
        self, method: APIMethod[T], **url_kw: Any
    ) -> T:
        request = method.build_request(**url_kw)
        raw_http_response = await self.send_request(
            request.endpoint,
            request.http_method,
            params=request.params,
            data=request.data,
            headers=request.headers,
            json=request.json_payload,
        )
        return method.parse_http_response(raw_http_response)

    async def get_json_content(
        self, request_params: RequestParams
    ) -> Dict[str, Any]:

        prepared_payload = make_payload(**request_params.__dict__)
        response = await self.send_request(**prepared_payload)
        return response.json()

    # async def get_json_content(
    #     self,
    #     url: str,
    #     method: str,
    #     cookies: Optional[LooseCookies] = None,
    #     json: Optional[Any] = None,
    #     data: Optional[Any] = None,
    #     headers: Optional[Any] = None,
    #     params: Optional[Any] = None,
    #     **kwargs: Any,
    # ) -> Dict[str, Any]:
    #     prepared_payload = make_payload(**locals(), exclude=("kwargs",))
    #     response = await self.send_request(**prepared_payload)
    #     return response.json()

    async def send_request(
        self, request_params: RequestParams
    ) -> HTTPResponse:
        session = await self._session_holder.get_session()
        return await self._session_holder.convert_third_party_lib_response_to_http_response(
            await session.request(
                method=request_params.method,
                url=request_params.url,
                data=request_params.data,
                headers=request_params.headers,
                json=request_params.json,
                cookies=request_params.cookies,
                params=request_params.params,
                **request_params.kwargs,
            )
        )

    # async def send_request(
    #     self,
    #     url: str,
    #     method: str,
    #     cookies: Optional[LooseCookies] = None,
    #     json: Optional[Any] = None,
    #     data: Optional[Any] = None,
    #     headers: Optional[Any] = None,
    #     params: Optional[Any] = None,
    #     **kwargs: Any,
    # ) -> HTTPResponse:
    #     session = await self._session_holder.get_session()
    #     return await self._session_holder.convert_third_party_lib_response_to_http_response(
    #         await session.request(
    #             method=method,
    #             url=url,
    #             data=data,
    #             headers=headers,
    #             json=json,
    #             cookies=cookies,
    #             params=params,
    #             **kwargs,
    #         )
    #     )

    async def warmup(self) -> Any:
        return await self._session_holder.get_session()

    async def shutdown(self) -> None:
        await self._session_holder.close()
