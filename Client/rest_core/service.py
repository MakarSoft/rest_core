import aiohttp
from typing import Optional, Union, Type, TypeVar
from .http_types import Protocol, ApiURL, API_URL
from .http_client import HTTPClient
from .session import Session
from .auth import Auth
from .resource import Action, Resource
from .http_headers import HttpHeaders
from .exceptions import ResourceNotAppendToApi
from pydantic import BaseModel

P = TypeVar("P", bound=BaseModel)
T = Union[P, list[P]]


class Service:
    '''
    Коллекция ресурсов сервиса
    Общая информация для всех ресурсов сервиса
    '''
    
    # ----------------------------------------------------------------
    def __init__(
        self,
        service: str, # имя сервиса
        headers: Optional[HttpHeaders] = None,  # Общие заголовки для всех ресурсов сервиса
    ) -> None:
        
        self.service = service

        # коллекция ресурсов присоединенных к сервису
        self.resources: dict[str, Resource] = {}

        # заголовки, используемые по умолчанию при доступе ко всем ресурсам сервиса
        self.headers = headers or HttpHeaders()
                
        



