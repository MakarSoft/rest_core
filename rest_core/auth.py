# ====================================================================
# rest_core/auth.py
# ====================================================================


import base64
import sys
import typing

from collections import namedtuple
from typing import Optional, Union, Literal


from .exceptions import ApiUsernameFormatError, ApiPasswordFormatError, ApiEncodingFormatError


AllowedEncoding = Literal['ascii', 'latin1']
TAuth = namedtuple('TAuth', ['login', 'password', 'encoding'])


# ====================================================================
# Auth
# ====================================================================
class Auth:
    """
    """
    
    def __init__(
        self,
        username: Optional[str]=None,
        password: Optional[str]=None,
        encoding: Optional[AllowedEncoding]='ascii'
    ) -> None:
        
        self.username = username
        self.password = password
        self.encoding = encoding

    # ----------------------------------------------------------------
    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(
        self,
        username: Optional[str]
    ) -> None:
        if username and not self._is_ascii_string(username):
            # имя указано, но использован не корректный набор символов
            raise ApiUsernameFormatError(f'Auth: Допустимо применение только ASCII-символов в имени пользователя, username = "{username}"')
        self._username = username

    # ----------------------------------------------------------------
    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(
        self,
        password: Optional[str]
    ) -> None:
        if password and not self._is_ascii_string(password):
            # пароль указан, но использован не корректный набор символов
            raise ApiPasswordFormatError('Auth: Допустимо применение только ASCII-символов в строке пароля...')
        self._password = password

    # ----------------------------------------------------------------
    @property
    def encoding(self) -> str:
        return self._encoding

    @encoding.setter
    def encoding(
        self,
        encoding: Optional[AllowedEncoding]
    ) -> None:
        if encoding and encoding in typing.get_args(AllowedEncoding):
            self._encoding = encoding
        else:
            raise ApiEncodingFormatError(f'Auth: Недопустимый параметр, encoding = {encoding}')
        
    # ----------------------------------------------------------------
    @property
    def auth_str(self) -> Optional[str]:
        '''
        Возвращает строковое представление аутентификационной информации
        '''
        
        string = None
        if all( attr and isinstance(attr, str) for attr in (self.username, self.password) ):
            string = base64.b64encode(
                bytes(
                    ':'.join( (self.username, self.password) ),
                    encoding='ascii'
                )
            ).decode()
        return string
    
    # ----------------------------------------------------------------
    @property
    def base_auth(self) -> Optional[str]:
        '''
        '''
        
        string = self.auth_str
        if string:
            string = f'Base {string}'
        return string

    # ----------------------------------------------------------------
    @property
    def auth(self) -> TAuth:
        '''
        Возвращает аутентификационную информацию в виде именнованного кортежа
        '''
        
        t_auth = TAuth(
            self.username,
            self.password,
            self.encoding
        )
        
        return t_auth

    # ----------------------------------------------------------------
    @staticmethod
    def _native_string(
        string_obj: Union[str, bytes, bytearray],
        encoding: Optional[AllowedEncoding] = 'ascii'
    ) -> Optional[str]:
        '''
        '''
        
        string = None
        
        if isinstance(string_obj, str):
            string = string_obj if encoding == sys.getdefaultencoding() else string_obj.encode().decode(encoding, errors='ignore')
        elif isinstance(string_obj, (bytes, bytearray)):
            string = string_obj.decode(encoding)
        
        return string

    # ----------------------------------------------------------------
    @staticmethod
    def _is_ascii_string(
        string: str
    ) -> bool:
        '''
        '''
        
        return isinstance(string, str) and string == string.encode().decode('ascii', errors='ignore')



# ====================================================================
