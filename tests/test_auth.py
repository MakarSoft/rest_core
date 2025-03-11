# tests/test_auth.py

# --------------------------------------------------------------------
# Тесты test_auth проверяют различные аспекты работы класса Auth, включая:
#
# Инициализацию объекта Auth.
# Установку и получение свойств username, password и encoding.
# Генерацию аутентификационной строки (auth_str).
# Форматирование базовой аутентификации (base_auth).
# Проверку на допустимость ASCII символов.
# Обработку ошибок при неправильных значениях.
#
# --------------------------------------------------------------------
# - запуск всех тестов из каталога tests:
#       pytest tests/
# - запуск файла тестов:
#      pytest tests/test_auth.py
# - запуск конкретной функции теста:
#       pytest tests/test_auth.py::test_auth_str
# - более подробный вывод (-v):
#       pytest -v tests/test_auth.py
# - остановить выполнение при первом сбое теста (-x)
#       pytest -x tests/test_auth.py
# --------------------------------------------------------------------

import pytest
from client.rest_core.auth import Auth
from client.rest_core.exceptions import (
    ApiEncodingFormatError,
    ApiAuthValueFormatError,
)


def test_auth_initialization() -> None:
    """
    Проверяет, что объект Auth правильно инициализируется
    с заданными значениями.
    """

    auth = Auth(username="user", password="pass", encoding="ascii")
    assert auth.username == "user"
    assert auth.password == "pass"
    assert auth.encoding == "ascii"


def test_auth_default_values() -> None:
    """
    Проверяет значения по умолчанию при инициализации без параметров.
    """

    auth = Auth()
    assert auth.username is None
    assert auth.password is None
    assert auth.encoding == "ascii"


def test_auth_username_setter() -> None:
    """
    Проверяет, что установка имени пользователя работает корректно.
    """

    auth = Auth()
    auth.username = "new_user"
    assert auth.username == "new_user"


def test_auth_password_setter() -> None:
    """
    Проверяет, что установка пароля работает корректно.
    """

    auth = Auth()
    auth.password = "new_pass"
    assert auth.password == "new_pass"


def test_auth_encoding_setter() -> None:
    """
    Проверяет, что установка кодировки работает корректно.
    """

    auth = Auth()
    auth.encoding = "latin1"
    assert auth.encoding == "latin1"


def test_auth_invalid_encoding() -> None:
    """
    Проверяет, что установка недопустимой кодировки вызывает ошибку.
    """

    auth = Auth()
    with pytest.raises(ApiEncodingFormatError):
        auth.encoding = "invalid_encoding"


def test_auth_username_invalid_ascii() -> None:
    """
    Проверяет, что установка имени пользователя с недопустимыми символами
    вызывает ошибку.
    """

    auth = Auth()
    with pytest.raises(ApiAuthValueFormatError):
        auth.username = "user_ñ"


def test_auth_password_invalid_ascii() -> None:
    """
    Проверяет, что установка пароля с недопустимыми символами вызывает ошибку.
    """

    auth = Auth()
    with pytest.raises(ApiAuthValueFormatError):
        auth.password = "pass_ñ"


def test_auth_str() -> None:
    """
    Проверяет, что метод auth_str возвращает правильную
    строку аутентификации в формате base64.
    """

    auth = Auth(username="user", password="pass")
    assert auth.auth_str == "dXNlcjpwYXNz"  # base64 encoding of "user:pass"


def test_base_auth() -> None:
    """
    Проверяет, что метод base_auth возвращает строку с префиксом "Base".
    """

    auth = Auth(username="user", password="pass")
    assert auth.base_auth == "Base dXNlcjpwYXNz"


def test_auth_tuple() -> None:
    """
    Проверяет, что метод auth возвращает правильный именованный кортеж.
    """

    auth = Auth(username="user", password="pass", encoding="ascii")
    assert auth.auth == ("user", "pass", "ascii")
