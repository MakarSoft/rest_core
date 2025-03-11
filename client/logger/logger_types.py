# ====================================================================
# Определение типов, используемых логером
#
# project/logger/logger_type
# ====================================================================

from __future__ import annotations

__all__ = [
    'LogFormatType',
    'LogLevel',
    'LoggerStyle',
    'FormatString',
    'DateFormatString'
]


import logging
from enum import Enum, IntEnum
from typing import Literal, NewType


LoggerStyle = Literal["%", "{"]
FormatString = NewType('FormatString', str)
DateFormatString = NewType('DateFormatString', str)


# TODO
# Разобраться с наследованием Enum от абстрактного класса... 

# ====================================================================
# ====================================================================
class LogFormatType(IntEnum):
    """
    степень детализации  формата
    """

    LOG_TINY = 0
    LOG_SHORT = 1
    LOG_MEDIUM = 2
    LOG_LONG = 3
    
    @classmethod
    def choices(cls) -> tuple[str, ...]:
        return tuple(cls._member_names_)

    @classmethod
    def default(cls) -> LogFormat:
        return cls.LOG_SHORT

    @classmethod
    def default_name(cls) -> str:
        return cls.default().name()

    @classmethod
    def default_val(cls) -> int:
        return cls.default().value

# ====================================================================
# ====================================================================
class LogLevel(IntEnum):
    """
    log level constants...
    """
    
    notset = logging.NOTSET
    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL

    @classmethod
    def choices(cls) -> tuple[str, ...]:
        return tuple(cls._member_names_)

    @classmethod
    def default(cls) -> LogLevel:
        return cls.warning

    @classmethod
    def default_name(cls) -> str:
        return cls.default().name.upper()

    @classmethod
    def default_val(cls) -> int:
        return getattr(logging, cls.default_name(), logging.WARNING)


# x = LogLevel.info
# print(x)
# print(type(x))
# print(type(x.value))
# print(type(x.name))
# print(x.name)
# print(LogLevel.choices())
# print(LogLevel['critical'])
# print(type(LogLevel['critical']))
# print(LogLevel.default())
# print(LogLevel.default().name)
# print(LogLevel.critical)
# print(LogLevel.default_val())