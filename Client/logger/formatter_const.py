# ====================================================================
# Определение типов, используемых логером
#
# project/logger/formatter_const
# ====================================================================

__all__ = [
    "DATE_FORMAT",
    "FORMAT_STYLE",
    "LOG_FORMAT",
    "DEBUG_FORMAT",
    "INFO_FORMAT",
    "WARNING_FORMAT",
    "ERROR_FORMAT",
    "CRITICAL_FORMAT",
    "DEFAULT_FORMAT",
    "DEF_FORMAT",
    "MSG_TEMPLATE"
]

import logging

from typing import Final

# Типы, используемые логгером...
from . import (
    LogFormatType,
    LogLevel,
    LoggerStyle,
    FormatString
)

# Формат даты
DATE_TIME_FORMAT: Final[str] = '%Y/%m/%d, %H:%M:%S'

# Дефолтовый стить фортата
FORMAT_STYLE: Final[LoggerStyle]  = '{'

format_config = '[%(module)s][ln:%(lineno)d][%(funcName)s][%(asctime)s.%(msecs)d]\n    %(levelname)s: %(message)s'
alt_format_config = '[%(asctime)s.%(msecs)d][%(funcName)s][%(module)s][ln:%(lineno)d]\n    %(levelname)s: %(message)s'

# Форматы по степени детализации информации...
# -----------------------------------------------
# LOG_FORMAT = {
#     LogFormatType.LOG_TINY: {
#         "%": "%(levelname)s:%(name)s %(message)s",
#         "{": "{levelname}:{name} {message}"
#     },
#     LogFormatType.LOG_SHORT: {
#         "%": "[%(asctime)s %(levelname)-8s %(name)-8s] [%(module)s:%(funcName)] %(message)s",
#         "{": "[{asctime} {levelname:<8} {name:<8}] [{module}:{funcName}] {message}"
#     },
#     LogFormatType.LOG_MEDIUM: {
#         "%": "[%(asctime)s %(levelname)-8s %(name)-8s] [%(module)s:%(funcName)s:%(lineno)03d] %(message)s",
#         "{": "[{asctime} {levelname:<8} {name:<8}] [{module}:{funcName}:{lineno:03d}] {message}"
#     },
#     LogFormatType.LOG_LONG: {
#         "%": "[%(asctime)s %(levelname)-8s %(name)-8s] [%(process)d::%(module)s:%(funcName)s:%(lineno)03d] %(message)s",
#         "{": "[{asctime} {levelname:<8} {name:<8}] [{process}::{module}:{funcName}:{lineno:03d}] {message}"
#     },
# }

LOG_FORMAT = {
    LogFormatType.LOG_TINY: {
        "%": "%(levelname)s:%(name)s %(message)s",
        "{": "{levelname}:{name} {message}"
    },
    LogFormatType.LOG_SHORT: {
        "%": "[%(asctime)s] [%(name)s:%(module)s:%(funcName)]:\n    %(levelname)-8s: %(message)s",
        "{": "[{asctime}] [{name}:{module}:{funcName}]:\n    {levelname:<8}: {message}"
    },
    LogFormatType.LOG_MEDIUM: {
        "%": "[%(asctime)s] [ %(name)s:%(module)s:%(funcName)s:%(lineno)03d]:\n    %(levelname)-8s: %(message)s",
        "{": "[{asctime}] [{name}:{module}:{funcName}:{lineno:03d}]:\n    {levelname:<8}: {message}"
    },
    LogFormatType.LOG_LONG: {
        "%": "[%(asctime)s] [%(name)s:%(process)d::%(module)s:%(funcName)s:%(lineno)03d]:\n    %(levelname)-8s: %(message)s",
        "{": "[{asctime}] [{name}({process})::{module}:{funcName}:{lineno:03d}]:\n    {levelname:<8}: {message}"
    },
}
# Форматы по уровню (с какой степенью детализации отображать сообщения соответствующего уровня)...
LOG_LEVEL_FORMAT: dict[int, dict[LoggerStyle, FormatString]] = {
    LogLevel.debug: LOG_FORMAT[LogFormatType.LOG_MEDIUM],
    LogLevel.info: LOG_FORMAT[LogFormatType.LOG_SHORT],
    LogLevel.warning: LOG_FORMAT[LogFormatType.LOG_SHORT],
    LogLevel.error: LOG_FORMAT[LogFormatType.LOG_LONG],
    LogLevel.critical: LOG_FORMAT[LogFormatType.LOG_LONG]
}

DEBUG_FORMAT: dict[LoggerStyle, FormatString] = LOG_LEVEL_FORMAT[LogLevel.debug]
INFO_FORMAT: dict[LoggerStyle, FormatString] = LOG_LEVEL_FORMAT[LogLevel.info]
WARNING_FORMAT: dict[LoggerStyle, FormatString] = LOG_LEVEL_FORMAT[LogLevel.warning]
ERROR_FORMAT: dict[LoggerStyle, FormatString] = LOG_LEVEL_FORMAT[LogLevel.error]
CRITICAL_FORMAT: dict[LoggerStyle, FormatString] = LOG_LEVEL_FORMAT[LogLevel.critical]

DEFAULT_FORMAT = LogFormatType.LOG_SHORT  # по умолчанию короткая форма 
DEF_FORMAT: dict[LoggerStyle, FormatString] = LOG_FORMAT[DEFAULT_FORMAT]


# Формат для сообщения
MSG_TEMPLATE: Final[str] = '===> {}: {}'

# log_messages = {
#     logging.DEBUG: f"{'DEBUG':=^50s}",
#     logging.INFO: f"{'INFO':=^50s}",
#     logging.WARNING: f"{'WARNING':=^50s}",
#     logging.ERROR: f"{'ERROR':=^50s}",
#     logging.CRITICAL: f"{'CRITICAL':=^50s}"
# }
