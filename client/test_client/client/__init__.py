# ====================================================================
# _HttpClient/client/__init__.py
# ====================================================================

from datetime import datetime
from typing import Optional, List

from _HttpClient.client.methods.bank_statement import GetBankStatement
from _HttpClient.client.methods.client_info import GetClientInfo
from _HttpClient.client.methods.exchange_rate_list import GetExchangeRates
from _HttpClient.client.methods.set_webhook import SetWebhook

from _HttpClient.core import BaseAPIClient
from _HttpClient.core.abc.base_api_client import RequestServiceFactoryType
from _HttpClient.core.request_service import (
    RequestServiceProto,
    RequestService,
)
from _HttpClient.core.session import AiohttpSessionHolder

from _HttpClient.types.bank_statement import BankStatement
from _HttpClient.types.client_info import ClientInfo
from _HttpClient.types.exchange_rate import ExchangeRate


# =====================================================================
# MonobankClient
# =====================================================================
class MonobankClient(BaseAPIClient):

    # ----------------------------------------------------------------
    def __init__(
        self,
        api_token: str,
        request_service_factory: Optional[RequestServiceFactoryType] = None,
    ):

        super().__init__(request_service_factory=request_service_factory)
        self._api_token = api_token

    # ----------------------------------------------------------------
    async def get_client_info(self) -> ClientInfo:
        return await self._request_service.execute_api_method(GetClientInfo())

    # ----------------------------------------------------------------
    async def get_exchange_rates(self) -> List[ExchangeRate]:
        return await self._request_service.execute_api_method(
            GetExchangeRates()
        )

    # ----------------------------------------------------------------
    async def set_webhook(self, url: str) -> bool:
        api_answer = await self._request_service.execute_api_method(
            SetWebhook(webhook_url=url)  # type: ignore
        )
        return api_answer["status"] == "ok"

    # ----------------------------------------------------------------
    async def get_bank_statement(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        account: int = 0,
    ) -> BankStatement:
        return await self._request_service.execute_api_method(
            GetBankStatement(
                from_date=from_date, account=account, to_date=to_date
            )
        )

    # ----------------------------------------------------------------
    async def _create_request_service(self) -> RequestServiceProto:
        return RequestService(
            session_holder=AiohttpSessionHolder(
                headers={"X-Token": self._api_token}
            )
        )
