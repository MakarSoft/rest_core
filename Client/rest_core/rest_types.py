# ====================================================================
# rest_core/rest_types.py
# ====================================================================

import re

from enum import Enum
from collections import namedtuple
from urllib.parse import urljoin

from typing import Literal, Optional, Union, get_args, get_origin
from pydantic import BaseModel, validator, IPvAnyAddress

from project.rest_core.exceptions import ApiUrlError


# Для валидации имени хоста ...
ALLOWED_FQDN_REGEXSTR = r"^((?![-])[-A-Z\d]{1,63}(?<!-)[.])*(?!-)[-A-Z\d]{1,63}(?<!-)[.]?$"
ALLOWED_FQDN_UNDERSCORES_REGEXSTR = r"^((?![-])[-_A-Z\d]{1,63}(?<!-)[.])*(?!-)[-_A-Z\d]{1,63}(?<!-)[.]?$"
# ALLOWED_REGEXSTR = r"^[a-z0-9]([a-z-0-9-]{0,61}[a-z0-9])?$"
# ALLOWED_REGEXSTR = r"(?!-)[A-Z\d-]{1,63}(?<!-)$"


# ====================================================================
# REST_URL
# ====================================================================
REST_URL = namedtuple(
    "API_URL",
    [
        'protocol',
        'host',
        'service'
    ]
)


# ====================================================================
# Protocol
# ====================================================================
AllowedProtocol = Literal['http', 'https']
class Protocol(Enum):
    HTTP = 'http'
    HTTPS = 'https'


# ====================================================================
# Method
# ====================================================================
AllowedMethod = Literal['GET', 'PUT', 'POST', 'DELETE']
class Method(Enum):
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'


# ====================================================================
# IpModel
# ====================================================================
class IpModel(BaseModel):
    ip: IPvAnyAddress


# ====================================================================
# ApiURL
# ====================================================================
class ApiURL(BaseModel):
    """
    """
    
    protocol: Protocol
    host: str
    service: Optional[str] = None
    
    #TODO - добавить валидацию каждого элемента ...
    def url(self) -> str:
        api_url = f'{self.protocol.value}://{self.host}'
        if self.service:
            api_url = f'{api_url}/{self.service}'
        return api_url
    

# ====================================================================
# RestURL
# ====================================================================
class RestURL():
    """
    """
    
    def __init__(
        self,
        protocol: Union[Protocol, AllowedProtocol],
        host: str,
        service: Optional[str] = None            
    ) -> None:
        
        self.protocol = protocol
        self.host = host
        self.service = service
        
    @property
    def base_url(self) -> str:
        return f'{self.protocol}://{self.host}'

    @property
    def api_url(self) -> str:
        url = self.base_url
        if self.service:
            # url = f'{url}/{self.service}'
            url = urljoin(url, self.service)
        return url
    
    @property
    def protocol(self) -> str:
        return self._protocol

    @protocol.setter
    def protocol(
        self,
        protocol: Union[Protocol, AllowedProtocol]
    ) -> None:
        msg = 'Недопустимый формат протокола: {}'

        if isinstance(protocol, Protocol):
            self._protocol = protocol.value
        elif isinstance(protocol, str) and protocol in get_args(AllowedProtocol):
            self._protocol = protocol
        else:
            raise ApiUrlError(msg.format(protocol))
            
    @property
    def host(self) -> str:
        return self._host
        
    @host.setter
    def host(self, host: str) -> None:
        msg = 'Недопустимый формат поля host: {}'
        
        if isinstance(host, str):
            host = host.strip('/')  # убираем лишнее
            try:
                ip: IpModel = IpModel(ip=host)
            except ValueError as e:
                # не ip-адрес - проверяем fqdn
                if not self.is_valid_fqdn(host):
                    raise ApiUrlError(msg.format(host))
        else:
            raise ApiUrlError(msg.format(host))
        
        self._host = host
        
    @property
    def service(self) -> str:
        return self._service
    
    @service.setter
    def service(self, service: Optional[str]) -> None:
        msg = 'Недопустимый формат строки сервиса: {}'
    
        if service is not None:
            # если сервис указан - это может быть только строка
            # формат не проверяем...
            if isinstance(service, str):
                service = service.strip('/')
            else:
                raise ApiUrlError(msg.format(service))
        self._service = service


    # --------------------------------------------------------------------
    # is_valid_fqdn
    # --------------------------------------------------------------------
    @staticmethod
    def is_valid_fqdn(hostname: str) -> bool:
        '''
        проверка переданной строки на корректность формата fqdn
        '''
        
        if not 1 < len(hostname) < 253:
            return False

        if hostname[-1] == '.':
            hostname = hostname[0:-1]

        labels = hostname.split('.')

        #  Определяем шаблон для DNS элемента
        #  Должен начинаться и заканчиваться только цифрой или буквой
        #  может содержать: [-, a-z, A-Z, 0-9]
        #  допустимо от 1 до  63 символов
        allowed = re.compile(
            ALLOWED_FQDN_REGEXSTR,
            re.IGNORECASE
        )

        # проверка всех элементов
        return all(allowed.match(label) for label in labels)

# ====================================================================
