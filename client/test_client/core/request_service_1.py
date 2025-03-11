import logging
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Optional,
    TypeVar,
    Union,
    List,
    Protocol,
)

from aiohttp.typedefs import LooseCookies

from _HttpClient.core.abc.api_method import APIMethod
from _HttpClient.core.session.holder import (
    AbstractSessionHolder,
    AiohttpSessionHolder,
    HTTPResponse,
)

# from _HttpClient.utils.compat import Protocol
# from _HttpClient.utils.payload import make_payload

logger = logging.getLogger("RequestService")

T = TypeVar("T")


@dataclass
class RequestParams:
    url: str
    method: str
    cookies: Optional[LooseCookies] = None
    json: Optional[Union[Dict[str, Any], List[Any]]] = None
    data: Optional[Union[Dict[str, Any], List[Any], str]] = None
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Union[str, int, float]]] = None
    kwargs: Optional[Dict[str, Any]] = None


class RequestServiceProto(Protocol):

    async def execute_api_method(
        self, method: APIMethod[T], **url_kw: Any
    ) -> T: ...

    async def get_json_content(
        self, request_params: RequestParams
    ) -> Dict[str, Any]: ...

    async def send_request(
        self, request_params: RequestParams
    ) -> HTTPResponse: ...

    async def warmup(self) -> Any: ...

    async def shutdown(self) -> None: ...


class RequestService:

    def __init__(
        self, session_holder: Optional[AbstractSessionHolder[Any]] = None
    ) -> None:
        self._session_holder = session_holder or AiohttpSessionHolder()

    async def execute_api_method(
        self, method: APIMethod[T], **url_kw: Any
    ) -> T:
        logger.debug(f"Executing API method: {method.__class__.__name__}")
        try:
            request = method.build_request(**url_kw)
            raw_http_response = await self.send_request(
                RequestParams(
                    url=request.endpoint,
                    method=request.http_method,
                    params=request.params,
                    data=request.data,
                    headers=request.headers,
                    json=request.json_payload,
                )
            )
            logger.debug(
                f"API method {method.__class__.__name__} executed successfully"
            )
            return method.parse_http_response(raw_http_response)
        except Exception as e:
            logger.error(f"Error executing API method: {e}")
            raise

    async def get_json_content(
        self, request_params: RequestParams
    ) -> Dict[str, Any]:
        response = await self.send_request(request_params)
        return await response.json()

    async def warmup(self) -> Any:
        return await self._session_holder.get_session()

    async def shutdown(self) -> None:
        await self._session_holder.close()

    async def send_request(
        self, request_params: RequestParams
    ) -> HTTPResponse:
        async with await self._session_holder.get_session() as session:
            try:
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
