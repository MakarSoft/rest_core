# ====================================================================
# rest_client.py
# ====================================================================

from __future__ import annotations

import aiohttp
import yarl


from collections import namedtuple
from pydantic import BaseModel

from typing import Optional, Union, TypeVar
from types import MethodType


from project.logger.logger_config import get_logger_config

from project.schemas import Response

from project.rest_core.rest_types import RestURL
from project.rest_core.auth import Auth

from project.rest_core.http_client import HTTPClient
from project.rest_core.http_headers import HttpHeaders
from project.rest_core.rest_types import Protocol, RestURL, REST_URL

from project.rest_core.session import Session, TOTAL_TIMEOUT
# from core.service import Service
from project.rest_core.resource import Action, Resource

    
UrlParts = namedtuple('UrlParts', ['resource_path', 'action_path_part'])

P = TypeVar("P", bound=BaseModel)
T = Union[P, list[P]]

logger =  get_logger_config()

# ====================================================================
# RestClient
# ====================================================================
class RestClient(HTTPClient):

    def __init__(
        self,
        *,
        protocol: Protocol,
        host: str,
        service: str,   # имя сервиса
        session: Optional[Session] = None,
        headers: Optional[HttpHeaders] = None,
        auth: Optional[Auth] = None,
    ) -> None:

        self.protocol = protocol
        self.host = host

        # имя сервиса
        self.service = service

        # коллекция ресурсов присоединенных к сервису
        self.resources: dict[str, Resource] = {}

        # Инициализация сессия, в рамках которой производятся все запросы к сервису API
        self.__session_must_be_closed = False
        if not session:
            # Если сессия не передается при инициализации инстанса, то создаём динамически 
            self.__session_must_be_closed = True
            session = Session(
                timeout = aiohttp.ClientTimeout(total=TOTAL_TIMEOUT)
            )

        if isinstance(auth, Auth):
            basic_auth = aiohttp.BasicAuth(*auth.auth) 
                   
        super().__init__(
            session,
            url = self.make_url(),
            auth = basic_auth,
            headers = headers
        )

    # ----------------------------------------------------------------
    # make_url
    # ----------------------------------------------------------------
    def make_url(self) -> Optional[str]:
        '''
        Сформированное строковое представление URL API
        '''
        
        rest_url = None
        if self.host:
            rest_url = RestURL(
                **REST_URL(self.protocol, self.host, self.service)._asdict()
            )
        
        url: Optional[str] = None
        if rest_url:
            url = rest_url.api_url
        
        return url            

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __del__(self) -> None:
        if self.__session_must_be_closed:
            self.session.close()
        
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def add_resource(
        self,
        res: Resource
    ) -> None:
        '''
        Добавление ресурса в список ресурсов API
        '''
        
        if isinstance(res, Resource):
            self.resources[res.name] = res

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def remove_resource(
        self,
        res_name: str
    ) -> Optional[Resource]:
        '''
        '''
        
        res = None
        if res_name in self.resources:
            res = self.resources.pop(res_name)
        return res
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_resource(
        self,
        resource_name: str
    ) -> Optional[Resource]:
        '''
        Возвращает объект ресурса по его имени
        или None, если  ресурс с указанным именем не присоединен к Api
        '''
        
        return self.resources.get(resource_name)
        
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def _build_url_parts(
            self,
            resource_name: str,
            action_name: str
    ) -> UrlParts:
    
        resource = self.get_resource(resource_name)
        if not resource:
            return UrlParts(None, None)
        return UrlParts(
            resource.path,
            resource.get_action_path_part(action_name)
        )
    
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_resource_path(
        self,
        resource_name: str
    ) -> Optional[str]:
        '''
        Возвращает части url, соответствующей ресурсу
        или None, если  ресурс с указанным именем не присоединен к Api-сервису
        или путь к ресурсу не прописан...
        '''
        
        resource: Optional[Resource] = self.get_resource(resource_name)
        resource_path = None
        if resource:
            resource_path = resource.resource_path

        # if not resource:
        #     raise ResourceNotAppendToApi(f'Не найден запрашиваемый Api-ресурс "{resource_name}"...')            
        return resource_path    

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_resource_action(
        self,
        resource_name: str,
        action_name: str
    ) -> Optional[Action]:
        '''
        Возвращает объекта Action
        или None,
            если ресурс с указанным именем не присоединен к Api-сервису
            или если к ресурсу не присоединена Активность с указанным именем
        '''
        
        resource: Optional[Resource] = self.get_resource(resource_name)
        act = None
        if resource:
            act = resource.get_action(action_name)
        
        # if not resource:
        #     raise ResourceNotAppendToApi(f'Не найден запрашиваемый Api-ресурс "{resource_name}"...')              
        return act    
          
    # ----------------------------------------------------------------
    # resource_endpoint
    # ----------------------------------------------------------------
    def resource_endpoint(
        self,
        resource_name: str
    ) -> Optional[str]:
        '''
        Полный адрес ресурса endpoint формируется из базового адреса api и
        часть пути по данным из описателя конкретного ресурса.
        Является основой для формирования URI
        '''
        
        resource = self.get_resource(resource_name)
        
        endpoint = resource.resource_path if resource else None
        if self.url:
            endpoint = '/'.join( ( self.url, endpoint ) ) if endpoint else self.url
        
        return endpoint
    
    # ----------------------------------------------------------------
    # get_url_part
    # ----------------------------------------------------------------
    def get_url_part(
        self,
        resource_name: str,
        action_name: str,
        obj_name: Optional[str] = None,
        *args
    ) -> Optional[str]:
        '''
        '''
    
        resource = self.get_resource(resource_name)
        
        # UrlParts = namedtuple('UrlParts', ['resource_path', 'action_path_part'])  
        url_parts = UrlParts(
            resource.path,
            resource.get_action_path_part(action_name, obj_name, *args)
        ) if resource else (None, None)
        
        url_part = url_parts.action_path_part
        if url_parts.resource_path:
            url_part = '/'.join(
                (
                    url_parts.resource_path,
                    url_parts.action_path_part
                )
            ) if url_parts.action_path_part else url_parts.resource_path
       
        return url_part 
    
    # ----------------------------------------------------------------
    # request
    # ----------------------------------------------------------------
    async def request(
        self,
        resource_name: str,
        action_name: str,
        obj_name: Optional[str]=None,
        *args,
        
        auth: Optional[aiohttp.BasicAuth] = None,
        headers: Optional[HttpHeaders] = None,        
        params: Optional[dict[str, str]] = None,
        payload: Optional[dict[str, Union[str, int, float]]] = None,
        response_model: P
    ) -> Optional[P]:
        '''
        '''        

        ret = None
        res = self.get_resource(resource_name)
        if res:
            method = res.get_method(action_name).value
            
            # параметры для формирования запроса...
            url_part = self.get_url_part(resource_name, action_name, obj_name, *args)
            # заголовки запроса
            headers = self.headers + res.headers + res.get_headers(action_name)
            
            try:
                ret = await self.make_request(
                    method=method,
                    url_part=url_part,
                    auth=auth,
                    headers=headers,
                    params=params,
                    payload=payload,
                    response_model=response_model
                )
            except Exception as exception:
                logger.error(
                    f'=== Client error ===\n   details:\n{exception}\n\n'
                )
                raise(exception)

            # Анализ ответа и преобразование типа....
            # response_model=response_model

        return ret

    # ----------------------------------------------------------------
    # add_action_method
    # TODO
    # ----------------------------------------------------------------
    def add_action_method(
        self,
        resource_name: str,
        action_name: str
    ) -> None:
        '''
        TODO ................
        response_model - привязать к активности
        '''
        
        async def action_method(
            self,
            # resource_name: str,
            # action_name: str,
            *parts,
            auth: Optional[aiohttp.BasicAuth] = None,
            headers: Optional[HttpHeaders] = None,        
            params: Optional[dict[str, str]] = None,
            payload: Optional[dict[str, Union[str, int]]] = None,
            response_model: P,
            **kwargs
        )-> Optional[P]:
            ret = await self.request(
                resource_name,
                action_name,
                *parts,
                auth = auth,
                headers = headers,        
                params = params,
                payload = payload,
                response_model = response_model
            )
            return ret
        
        if self.client:
            res = self.get_resource(resource_name)
            action = res.get_action(action_name)
            if action:
                # name = f'{res.name}_{action_name}'
                name = f"{action_name.replace('-','_')}"
        setattr(self, name, MethodType(action_method, self))
    
