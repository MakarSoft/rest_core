# ====================================================================
# resource.py
# ====================================================================

import sys

from collections.abc import Iterable
from pydantic import BaseModel

from project.schemas import Response

   
from typing import (
    Any,
    Optional,
    Union,
    TypeVar,
    Literal,
    Mapping,
    TypedDict
)

# if sys.version_info >= (3,11):
#     from typing import NoRequired, Required


from project.rest_core.exceptions import (
    ApiActionNotFound,
    ApiInternalError,
    ActionURLMatchError
)

from project.rest_core.http_headers import (
    HeadersItem,
    HttpHeaders
)

from project.rest_core.rest_types import Method

from project.rest_core.action import (
    QueryParamValueType,
    QueryParams,
    ActionDict,
    Action,
    ActionModel
)


P = TypeVar("P", bound=BaseModel)


# ====================================================================
# ResourceDict
# ====================================================================
if sys.version_info >= (3,10):
    
    class ResourceDict(TypedDict):
        """
        """

        name: str
        path: str
        actions: Iterable[ActionDict]
        
        headers: Optional[HeadersItem]
        path_params: Optional[Iterable[str]] 
        query_params: Optional[QueryParams]    

else:

    class _ResourceDict(TypedDict):
        """
        """

        name: str
        path: str
        actions: Iterable[ActionDict]
        
    class ResourceDict(_ResourceDict, total=False):
        """
        """

        headers: Optional[HeadersItem]
        path_params: Optional[Iterable[str]] 
        query_params: Optional[QueryParams]


    
# ====================================================================
# ResourceModel
# ====================================================================
class ResourceModel(BaseModel):
    """
    """

    name: str
    path: Optional[str]
    path_params: Optional[Iterable[str]]=None
    query_params: Optional[Iterable[tuple[str, QueryParamValueType]]]=None
    headers: Optional[Iterable[HeadersItem]] = None
    actions: Iterable[ActionModel]


# ====================================================================
# Resource
# ====================================================================
class Resource:
    """
    """

    def __init__(
        self,
        name: str,
        *,
        headers: Optional[HttpHeaders] = None,      
        path: str,
        path_params: Optional[Iterable[str]] = None,
        query_params: Optional[Iterable[tuple[str, QueryParamValueType]]] = None
    ) -> None:

        self.name = name
        
        self.headers = headers or HttpHeaders()
        self.path = path
        self.query_params = query_params
        self.path_params = path_params

        self.actions: dict[str, Action] = {} # таблица активностей для данного ресурса

    # ----------------------------------------------------------------
    # add_action
    # ----------------------------------------------------------------
    def add_action(
        self,
        act: Action
    )-> None:
        '''
        '''
        
        if isinstance(act, Action):
            name = act.name
            if name:
                self.actions[name] = act
            
    # ----------------------------------------------------------------
    # create_action
    # ----------------------------------------------------------------
    def create_action(
        self,
        name: str,
        method: Method,
        *,
        path: str,
        path_params: Optional[Iterable[str]] = None, 
        query_params: Optional[dict[str, type]] = None,
        headers: Optional[HttpHeaders] = None,
        response_model: P = Response,
        objects: Optional[list[ActionModel]] = None
    )-> Action:
        '''
        Создание объекта Action и добавление его в
        соответствующую Mapping-коллекцию данного ресурса
        '''
        
        action = Action(
            name = name,
            method = method,
            path = path,
            path_params = path_params,
            query_params = query_params,
            headers = headers or HttpHeaders(),
            response_model = response_model, 
            objects = objects or []
            
        )
        
        self.actions[name] = action
        return action

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_action(
        self,
        action_name: str,
        action_map: Mapping[str, Action] = None
    ) -> Optional[Action]:
        '''
        Получение объекта-значения из Mapping-коллекции по строковому ключу (action_name)
        В случае отсутствия ключа в Mapping-коллекции - None
        '''
        
        action = None
        
        if isinstance(action_name, str):
            if not action_map:
                action_map = self.actions
            action = action_map.get(action_name)
            
        return action
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_action_attr(
        self,
        action_name: str,
        action_attr_name: str
    ) -> Any:
        '''
        Метод должен вызываться через методы-обертки
        со статически заданным именем атрибута attr_name
        '''
            
        action = self.get_action(action_name)
        if not action:
            raise ApiActionNotFound(f'Не найден объект активности {action_name}...')
        
        try:
            res = getattr(action, action_attr_name)
        except AttributeError as exception:
            raise ApiInternalError(
                f'Задан недопустимое имя атрибута "{action_attr_name}" для объекта "{type(action).__name__}"'
            ) from exception
        
        return res
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_name(self, action_name) -> Method:
        return self.get_action_attr(action_name, 'name')
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_method(self, action_name) -> Method:
        return self.get_action_attr(action_name, 'method')
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_path_template(self, action_name) -> Optional[str]:
        return self.get_action_attr(action_name, 'path_template')

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_response_model(self, action_name) -> P:
        return self.get_action_attr(action_name, 'response_model')

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_headers(self, action_name) -> Optional[HttpHeaders]:
        return self.get_action_attr(action_name, 'headers')

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_path_params_part(
        self,
        action_name: str,
        *parts
    ) -> Optional[str]:
        '''
        '''
        
        path_params_patr = None
        
        if not parts:
            parts = self.path_params
        path_template = self.get_path_template(action_name)
        if path_template:
            path_params_patr = path_template
            if parts:
                try:
                    path_params_patr = path_template.format(*parts)
                except IndexError as exception:
                    raise ActionURLMatchError(f'No url match for "{action_name}"') from exception
        elif parts:
            path_params_patr = '/'.join(parts)
                
        return path_params_patr

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_action_path_part(
        self,
        action_name: str,
        obj_name: Optional[str],
        *args
    ) -> Optional[str]:
        '''
        '''
        
        url_part: Optional[str] = None
        
        action = self.get_action(action_name)
        if action:
            
            # базовой частью для url активности считаем имя активности
            url_part = action.name  
            
            # генерация части url, связанной с параметрами пути
            parts = args    # args -> список параметров
                            # явно переданные параметры пути имеют приоритет
            if not parts:
                # параметры не переданы - проверяем параметры, указанные в структуре данных активности
                parts = action.path_params

            if not parts:
                # посмотреть общие параметры ресурса
                parts = self.path_params
                
            params_part: Optional[str] = None  # часть url, определяемая заданными параметрами
            # если path указан, он будет использован как шаблон при обработки параметров пути
            if parts and isinstance(parts, Iterable) and all(isinstance(x, str) for x in parts):
                # параметры есть, есть ли шаблон для формирования их представления
                if action.path:
                    # шаблон задан - пытаемся сформировать представление параметров пути
                    try:
                        params_part = action.path.format(*parts)
                    except IndexError as exception:
                        raise ActionURLMatchError(f'No url match for "{action_name}"') from exception
                else:
                    # шаблон не указан - формируем представление по умолчанию...
                    params_part = '/'.join(parts)

            if params_part:
                url_part = f'{url_part}/{params_part}'

            obj = action.get_obj(obj_name)
            if obj:
                url_part = f'{url_part}/{obj.name}'
            
        return url_part

    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_path(
        self
    ) -> Optional[str]:
        '''
        Возвращает части url, соответствующей ресурсу
        '''
            
        return self.resource_path

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_action(
        self,
        action_name: str
    ) -> Optional[Action]:
        '''
        Возвращает объекта Активности
        '''
        
        return self.actions.get(action_name)    
