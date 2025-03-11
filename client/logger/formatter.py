# ====================================================================
# Настройка форматтера
# 
# project/logger/formatter.py
# ====================================================================

__all__ = ["LogFormatter" ,"LevelFormatter"]

import logging

from datetime import datetime
from typing import Optional, Mapping


from .formatter_const  import (
    DATE_TIME_FORMAT,
    FORMAT_STYLE,
    LOG_FORMAT,
    DEBUG_FORMAT,
    INFO_FORMAT,
    WARNING_FORMAT,
    ERROR_FORMAT,
    CRITICAL_FORMAT,
    DEF_FORMAT,
    LOG_LEVEL_FORMAT,
    MSG_TEMPLATE
)
from .logger_types  import (
    LogFormatType,
    LogLevel,
    LoggerStyle,
    FormatString,
    DateFormatString
)
    
# ====================================================================
# ====================================================================

def get_now_str() -> str:
    return datetime.now().strftime(DATE_TIME_FORMAT)



# ====================================================================
# ====================================================================
class LogFormatter(logging.Formatter):
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: str = DATE_TIME_FORMAT,
        style: LoggerStyle = FORMAT_STYLE,
        validate: bool = True
    ) -> None:
   
        self.style = style
        fmt = DEFAULT_FORMAT[style] if fmt is None else fmt

        super().__init__(fmt, datefmt, style, validate)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def formatMessage(
        self,
        record: logging.LogRecord
    ) -> str:
        # балванка для дальнейшего расширения ....

        message = super().formatMessage(record)
        return message


    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def formatTime(
        self,
        record: logging.LogRecord,
        datefmt: str = None
    ) -> str :
        
        if datefmt is None:
            datefmt =  self.datefmt
        
        s = super().formatTime(record, datefmt)

        return s


    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def format(
        self,
        record: logging.LogRecord
    ) -> str :
    
        self._fmt = LOG_LEVEL_FORMAT.get(record.levelno, DEF_FORMAT)[self.style]

        s = super().format(record)

        return s


# ====================================================================
# ====================================================================
class LevelFormatter():
    """
    Расширение LogFormatter, использующее свои строки форматирования для каждого уровня.
    """

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __init__(
        self,
        fmt: dict[int, dict[LoggerStyle, FormatString]],
        datefmt: Optional[str] = None,
        style: LoggerStyle = FORMAT_STYLE,
        validate: bool = True        
    ) -> None:

        self.formatters = {
            level: LogFormatter(format_dict[style], datefmt, style, validate)
            for level, format_dict in fmt.items()
        }

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def format(
        self,
        record: logging.LogRecord
    ) -> str:

        formatter: LogFormatter = self.formatters[record.levelno]
        log_str = formatter.format(record)

        return log_str

# class LevelFormatter:
#     def __init__(
#         self,
#         fmt: Mapping[int, str],
#         **kwargs
#     ) -> None:
#         self.formatters = {
#             level: LogFormatter(fmt=format_str, **kwargs) for level, format_str in fmt.items()
#         }
#     def format(self, record: logging.LogRecord) -> str:
#         formatter: LogFormatter = self.formatters[record.levelno]
#         log_str = formatter.format(record)
#         return log_str
