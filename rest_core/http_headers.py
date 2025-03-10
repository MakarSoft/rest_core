# ====================================================================
# rest_core/http_headers.py
# ====================================================================

import copy
import sys

from typing import Optional, Union
from collections.abc import Iterable, Mapping

if sys.version_info >= (3,10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias
    
    
# ====================================================================
# HeadersItem
# ====================================================================
HeadersItem: TypeAlias = Union[
    Iterable[tuple[str, str]],
    Mapping[str, str]
]


# ====================================================================
# HttpHeaders
# ====================================================================
class HttpHeaders:

    def_headers = {    
        'json': {
            'Content-Type': 'application/json'
            ,'Accept': 'application/json'
        },
        'yang':  {
            'Content-Type': 'application/yang-data+json'
            ,'Accept': 'application/yang-data+json'
        }
    }
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __init__(
        self,
        items: Optional[HeadersItem] = None
    ) -> None:
        self.headers = items
        
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __getattr__(self, name: str):
        if name == '_headers':
            setattr(self, name, {}) # self.__dict__[name] = {}
            return getattr(self, name)
    
    # ----------------------------------------------------------------
    # check_header_items
    # ----------------------------------------------------------------
    @staticmethod
    def check_header_items(
        items: HeadersItem
    ) -> bool:
        
        if ret := isinstance(items, Iterable):
            if isinstance(items, Mapping):
                items = items.items()
            ret = all(
                isinstance(item, tuple) and len(item) == 2 and  all(type(x) == str for x in item)
                for item in items
            )
        return ret
    
    # ----------------------------------------------------------------
    # compatible_obj
    # ----------------------------------------------------------------
    def compatible_obj(self, obj) -> Optional[HeadersItem]:
        compatible_obj = None
        if isinstance(obj, self.__class__):
            compatible_obj = obj.headers
        elif self.check_header_items(obj):
            compatible_obj = obj
        return compatible_obj
    
    # ----------------------------------------------------------------
    # __add__
    # ----------------------------------------------------------------
    def __add__(self, other):
        if (other := self.compatible_obj(other)) is None:
            raise ArithmeticError(f"Недопустимый тип аргумента {type(other)}")
        h = copy.deepcopy(self._headers)
        h.update(dict(other))
        return self.__class__(h)
            
    # ----------------------------------------------------------------
    # __radd__
    # ----------------------------------------------------------------
    def __radd__(self, other):
        return self + other
    
    # ----------------------------------------------------------------
    # __iadd__
    # ----------------------------------------------------------------
    def __iadd__(self, other):
        if not (other := self.compatible_obj(other)):
            raise ArithmeticError(f"Недопустимый тип аргумента {type(other)}")
        self._headers.update(dict(other))
        
        return self

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, items: Optional[HeadersItem]) -> None:
        self.init_headers(items)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def clear_headers(self) -> None:
        self._headers.clear()
        # self._headers = {}
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def update_header(
        self,
        items: Optional[HeadersItem] = None
    ) -> None:
        ''''''
        if items and self.check_header_items(items):
            self._headers.update(dict(items))

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def init_headers(
        self,
        items: Optional[HeadersItem] = None
    ) -> None:
        ''''''
        self.clear_headers()
        self.update_header(items)
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def init_json_headers(self) -> None:
        '''
        '''
        
        items = self.def_headers.get('json')
        if items:
            self.init_headers(items)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def init_yang_headers(self) -> None:
        '''
        '''
        
        items = self.def_headers.get('yang')
        if items:
            self.init_headers(items)
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_header_value(self, key: str) -> Optional[str]:
        '''
        '''
        
        item: Optional[str] = None
        if isinstance(self.headers, dict) and isinstance(key, str):
            item = self.headers.get(key)
        return item

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def set_header_value(self, key: str, item: str) -> None:
        '''
        '''
        
        if all(isinstance(x, str) for x in (key, item)):
            self.headers[key] = item
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def del_headers_item(self, key: str) -> None:
        '''
        '''
        
        if isinstance(self.headers, dict) and isinstance(key, str):
            if "Authorization" in self.headers:
                del self.headers["Authorization"]
                    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_content_type_header(self) -> Optional[str]:
        '''
        '''
        
        return self.get_header_value("Content-Type")

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def set_content_type_header(
        self,
        content_type: str = 'application/json'
    ) -> None:
        self.set_header_value("Content-Type", content_type)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_accept_header(self) -> Optional[str]:
        return self.get_header_value("Accept")

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def set_accept_header(
        self,
        accept: str = 'application/json'
    ) -> None:
        self.set_header_value("Accept", accept)
    
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_auth_header(self) -> Optional[str]:
        return self.get_header_value("Authorization")

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def set_auth_header(
        self,
        auth_str: str
    ) -> None:
        self.set_header_value("Authorization", auth_str)
    
# ====================================================================
