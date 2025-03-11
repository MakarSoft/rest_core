# ====================================================================
# rest_core/auth.py
# ====================================================================

import base64
import sys
import typing

from collections import namedtuple
from typing import Optional, Union, Literal, get_args


from .exceptions import (
    ApiUsernameFormatError,
    ApiPasswordFormatError,
    ApiEncodingFormatError,
)


AllowedEncoding = Literal["ascii", "latin1"]
TAuth = namedtuple("TAuth", ["login", "password", "encoding"])


# ====================================================================
# Auth
# ====================================================================
class Auth:
    """ """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        encoding: Optional[AllowedEncoding] = "ascii",
    ) -> None:

        self.username = username
        self.password = password
        self.encoding = encoding

    # ----------------------------------------------------------------
    @property
    def username(self) -> Optional[str]:
        return self._username

    @username.setter
    def username(self, username: Optional[str]) -> None:
        self._validate_ascii(username, "username")
        self._username = username

    # ----------------------------------------------------------------
    @property
    def password(self) -> Optional[str]:
        return self._password

    @password.setter
    def password(self, password: Optional[str]) -> None:
        self._validate_ascii(password, "password")
        self._password = password

    # ----------------------------------------------------------------
    @property
    def encoding(self) -> Optional[str]:
        return self._encoding

    @encoding.setter
    def encoding(self, encoding: Optional[AllowedEncoding]) -> None:
        if encoding and encoding in typing.get_args(AllowedEncoding):
            self._encoding = encoding
        else:
            raise ApiEncodingFormatError(
                f"Auth: Недопустимый параметр, encoding = {encoding}"
            )

    # ----------------------------------------------------------------
    @property
    def auth_str(self) -> Optional[str]:
        """
        Возвращает строковое представление аутентификационной информации
        """

        string = None
        if all(
            attr and isinstance(attr, str)
            for attr in (self.username, self.password)
        ):
            string = base64.b64encode(
                bytes(
                    ":".join((self.username, self.password)), encoding="ascii"
                )
            ).decode()
        return string

    # ----------------------------------------------------------------
    @property
    def base_auth(self) -> Optional[str]:
        """ """

        string = self.auth_str
        if string:
            string = f"Base {string}"
        return string

    @property
    def auth(self) -> TAuth:
        """
        Возвращает аутентификационную информацию в виде именнованного кортежа
        """

        t_auth = TAuth(self.username, self.password, self.encoding)

        return t_auth

    # ----------------------------------------------------------------
    @staticmethod
    def _validate_ascii(value: Optional[str], field_name: str) -> None:
        """
        Проверяет, является ли строка ASCII.
        """

        if value and not value.isascii():
            raise ApiUsernameFormatError(
                f'Auth: Допустимо применение только ASCII-символов в {field_name}, значение = "{value}"'
            )

    # ----------------------------------------------------------------
    @staticmethod
    def _native_string(
        string_obj: Union[str, bytes, bytearray],
        encoding: Optional[AllowedEncoding] = "ascii",
    ) -> Optional[str]:
        """
        Преобразует строку в соответствии с заданным кодированием.
        """

        if isinstance(string_obj, str):
            return (
                string_obj
                if encoding == sys.getdefaultencoding()
                else string_obj.encode().decode(encoding, errors="ignore")
            )
        elif isinstance(string_obj, (bytes, bytearray)):
            return string_obj.decode(encoding)
        return None

    @staticmethod
    def _native_string(
        string_obj: Union[str, bytes, bytearray],
        encoding: AllowedEncoding = "ascii",
    ) -> Optional[str]:
        """
        Преобразует строку в соответствии с заданным кодированием.
        """

        # Проверяем на допустимость значения encoding
        if encoding not in get_args(AllowedEncoding):
            raise ValueError(
                f"Недопустимое значение encoding: {encoding}. Допустимые значения: {valid_encodings}."
            )

        if isinstance(string_obj, str):
            return (
                string_obj
                if encoding == sys.getdefaultencoding()
                else string_obj.encode().decode(encoding, errors="ignore")
            )
        elif isinstance(string_obj, (bytes, bytearray)):
            return string_obj.decode(encoding)
        return None


# ====================================================================
