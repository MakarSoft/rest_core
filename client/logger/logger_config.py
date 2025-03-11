# ====================================================================
# 
#
# project/logger/logger_config.py
# ====================================================================

# TODO - сконфигурировать логер (по шаблону), как в словаре...

import logging
import logging.config

from project.logger.logger_dict_config import APP_NAME, LOG_CONFIG 

from . import (
    FORMAT_STYLE,
    DEF_FORMAT,
    DATE_TIME_FORMAT,
    LogLevel,
    LogFormatType,
    LoggerStyle,
    FormatString,
    DateFormatString
)


# ====================================================================
# ====================================================================
def init_file_handler(
    file: str,
    level: int = logging.DEBUG,
    format: dict[LoggerStyle, FormatString] = DEF_FORMAT,
    datefmt: DateFormatString = DATE_TIME_FORMAT,
    style: LoggerStyle = FORMAT_STYLE
) -> logging.Handler:
    
    file_handler = logging.FileHandler(file)
    file_handler.setLevel(level)
    fmt=format[style]
    file_handler.setFormatter(
        logging.Formatter(
            fmt=format[style],
            datefmt=datefmt,
            style=style
        )
    )

    return file_handler


# ====================================================================
# ====================================================================
def init_stream_handler(
    level: int = logging.DEBUG,
    format: dict[LoggerStyle, FormatString] = DEF_FORMAT,
    datefmt: DateFormatString = DATE_TIME_FORMAT,
    style: LoggerStyle = FORMAT_STYLE
) -> logging.Handler:
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(
        logging.Formatter(
            fmt=format[style],
            datefmt=datefmt,
            style=style
        )
    )

    return stream_handler


# ====================================================================
# ====================================================================
def get_logger(
    name: str,
    level: int,
    file: str
) -> logging.Logger:

    logger = logging.getLogger(name)

    logger.setLevel(level)

    logger.addHandler(init_file_handler(file))
    logger.addHandler(init_stream_handler())

    return logger

# ====================================================================
# ====================================================================
def get_logger_config(
    name: str = APP_NAME,
    logger_config: dict = LOG_CONFIG
) -> logging.Logger:

    logging.config.dictConfig(logger_config)
    logger = logging.getLogger(name)

    return logger