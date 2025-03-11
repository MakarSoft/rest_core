from typing import ClassVar, List

from _HttpClient.client.base import MonobankAPIMethod
from _HttpClient.types.exchange_rate import ExchangeRate


class GetExchangeRates(MonobankAPIMethod[List[ExchangeRate]]):
    url: ClassVar[str] = "https://api.monobank.ua/bank/currency"
    http_method: ClassVar[str] = "GET"
