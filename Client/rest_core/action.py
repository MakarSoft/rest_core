# ====================================================================
# rest_core/action.py
# ====================================================================

from __future__ import annotations

import sys

from typing import Optional, Union, TypeVar, Mapping

if sys.version_info >= (3,10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias
    
from typing import TypedDict
if sys.version_info >= (3,11):
    from typing import NoRequired, Required


from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, field_validator

from project.schemas import Response

from project.rest_core.http_headers import HeadersItem, HttpHeaders
from project.rest_core.rest_types import Method
from project.rest_core.utils import get_kwargs


# --------------------------------------------------------------------

P = TypeVar("P", bound=BaseModel)


# --------------------------------------------------------------------
# QueryParam
# --------------------------------------------------------------------
# Типы, связанные с описанием параметров запроса
# --------------------------------------------------------------------

QueryParamValueType: TypeAlias = Union[float, int, str]

QueryParams: TypeAlias = Union[
    Iterable[tuple[str, QueryParamValueType]],
    Mapping[str, QueryParamValueType]
]

    
# ====================================================================
# QueryParam
# ====================================================================
class QueryParam(BaseModel):
    '''
    '''
    
    param_name: str # имя параметра
    param_value: QueryParamValueType    # значение параметра


# ====================================================================
# ActionDict
# ====================================================================
if sys.version_info >= (3,10):

    class ActionDict(TypedDict):
        """
        name
        method
        objects
        path    если путь отсутствует - в качестве элемента пути используется имя активности
                если путь присутствует, то он интерпретируется как шаблон для подстановки
                параметров пути, tсли таковые имеются
        heagers
        response_model  response - если не указано или None - используем Response
        """
        
        name: str
        method: Method
        objects: list[ActionModel]
        path: NoRequired[Optional[str]]
        headers: NoRequired[Optional[HeadersItem]]
        response_model: NoRequired[Optional[P]]    # response - если не указано или None - используем Response

else:
    
    class _ActionDict(TypedDict):
        """
        """
        
        name: str
        method: Method
        objects: list[ActionModel]


    class ActionDict(_ActionDict, total=False):
        """
        """
        
        path: Optional[str]
        headers: Optional[HeadersItem]
        response_model: Optional[P]    # response - если не указано или None - используем Response
    

# ====================================================================
# ActionObject
# ====================================================================
class ActionObject(BaseModel):
    """
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    
    name: str
    query_params: Optional[Iterable[QueryParam]] = None
    response_model: Optional[type] = None
    
    @field_validator('response_model', mode='before')
    def type_validator(cls, value):
        # если value не указано или is None - используем Response
        # ???
        if not value:
            return Response
        if value and issubclass(value, BaseModel):
           return value
        raise ValueError("response_model type Error.")


# ====================================================================
# ActionModel
# ====================================================================
class ActionModel(BaseModel):
    """
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
   
    name: str 
    method: Method
    path: Optional[str] = None
    path_params: Optional[Iterable[str]] = None
    headers: Optional[HttpHeaders] = None
    response_model: Optional[type] = None   # класс для валидации ответа сервера
    objects: Optional[Iterable[Mapping[str, ActionObject]]]
    
    @field_validator('response_model', mode='before')
    def type_validator(cls, value):
        if not value:
            return Response
        if value and issubclass(value, BaseModel):
           return value
        raise ValueError("response_model type Error.")


# ====================================================================
# Action
# ====================================================================
class Action:
    """
    """
 
    def __init__(
        self,
        name: str,
        method: Method,
        *,
        path: Optional[str] = None,
        path_params: Optional[Iterable[str]] = None,            # параметры пути
        query_params: Optional[Iterable[QueryParam]] = None,    # параметры запроса
        headers: Optional[HttpHeaders] = None,
        response_model: P = Response,
        objects: Optional[list[ActionObject]] = None
    ):

        if isinstance(name, str) and isinstance(method, Method):
            self.name = name
            self.method = method
            self.path = path
            self.path_params = path_params
            self.query_params =  query_params
            self.headers = headers
            self.response_model = response_model
            if not objects:
                objects = {}
            self.objects: dict[str, ActionObject] = objects
        else:
            raise ValueError ('')
        
    # ----------------------------------------------------------------
    # add_object
    # ----------------------------------------------------------------
    def add_object(
        self,
        obj: ActionObject
    )-> None:
        '''
        '''
        
        if isinstance(obj, ActionObject):
            name = obj.name
            if name:
                self.objects[name] = obj
                    
    # ----------------------------------------------------------------
    # create_object
    # ----------------------------------------------------------------
    def create_object(
        self,
        *,
        name: str,   # имя объекта активности
        query_params: Optional[Iterable[QueryParam]] = None,
        response_model: Optional[type] = None
    ) -> Optional[ActionObject]:
        
        kwargs = get_kwargs()
        obj = ActionObject(**kwargs)
        if obj:
            self.objects[name] = obj

    # ----------------------------------------------------------------
    # get_obj
    # ----------------------------------------------------------------
    def get_obj(
        self,
        obj_name: Optional[str],
        obj_map: Optional[Mapping[str, ActionObject]] = None
    ) -> Optional[ActionObject]:
        '''
        '''
        
        obj = None
        
        if obj_name and isinstance(obj_name, str):
            if not obj_map:
                obj_map = self.objects
            obj = obj_map.get(obj_name)
        
        return obj        
        
# ====================================================================