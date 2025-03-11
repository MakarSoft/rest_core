# ====================================================================
# Конфигурация логгера в виде словаря...
# 
# project/logger/logger_dict_config.py
# ====================================================================

__all__ = ['LOG_CONFIG']

import logging
import sys


from project.config import LOG_DIR, APP_NAME

from .logger_types  import (
    LogFormatType,
    LogLevel,
    LoggerStyle,
    FormatString,
    DateFormatString
)


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

from .filters import (
    RequireDebugFalse,
    RequireDebugTrue,
    DebugOnly,
    InfoOnly,
    WarningsOnly,
    ErrorsOnly
)

from .formatter import (
    LogFormatter,
    LevelFormatter
)

APP_NAME = 'MY_APP'


# ====================================================================
# ====================================================================
LOG_CONFIG = {
    "version":1,
    'disable_existing_loggers': False,
    
    # Корневой регистратор ===========================================
    "root": {
        "handlers" : [
            "debug_handler_console",
            "info_handler_console",
            "debug_handler_file",
            "info_handler_file",
            "warnings_handler_file",
            "errors_handler_file",
            "all_handler_file",
        ],
        "level": LogLevel.default(),
        'propagate': True
    },

    # FILTERS ========================================================
    "filters": {
        "require_debug_true": {
            "()": RequireDebugTrue
        },
        "require_debug_false": {
            "()": RequireDebugFalse
        },
        "debug_filter":{
            "()": DebugOnly
        },
        "info_filter":{
            "()": InfoOnly
        },
        "warning_filter":{
            "()": WarningsOnly
        },
        "error_filter":{
            "()": ErrorsOnly
        }
    },    

    # FORMATTERS =====================================================
    "formatters": {
        "LevelFormatter": {
            "()": LevelFormatter,
            "style": FORMAT_STYLE,
            "format":  LOG_LEVEL_FORMAT,
            "datefmt": DATE_TIME_FORMAT
        },
        "default": {
            "()": LogFormatter,
            'style': FORMAT_STYLE,
            'format':  DEF_FORMAT[FORMAT_STYLE],
            "datefmt": DATE_TIME_FORMAT
        },
        # 'debug': {
        #     "()": LogFormatter,
        #     'style': FORMAT_STYLE,
        #     'format': DEBUG_FORMAT[FORMAT_STYLE],
        #     "datefmt": DATE_TIME_FORMAT
        # },
        # 'info': {
        #     "()": LogFormatter,
        #     'style': FORMAT_STYLE,
        #     'format': INFO_FORMAT[FORMAT_STYLE],
        #     "datefmt": DATE_TIME_FORMAT
        # },
        # 'warning': {
        #     "()": LogFormatter,
        #     'style': FORMAT_STYLE,
        #     'format': WARNING_FORMAT[FORMAT_STYLE],
        #     "datefmt": DATE_TIME_FORMAT
        # },
        # 'error': {
        #     "()": LogFormatter,
        #     'style': FORMAT_STYLE,
        #     'format': ERROR_FORMAT[FORMAT_STYLE],
        #     datefmt": DATE_TIME_FORMAT
        # }
    },
    
    # HANDLERS =======================================================
    "handlers": {
        'default': { 
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },        
        "debug_handler_console": {
            "level": logging.DEBUG
            ,"class": "logging.StreamHandler"
            ,"stream": sys.stdout  #sys.stderr
            ,"formatter": "LevelFormatter" #"debug"
            ,"filters": ["require_debug_true"]
        },
        "info_handler_console": {
            "level": logging.INFO
            ,"class": "logging.StreamHandler"
            ,"stream": sys.stdout  #sys.stderr
            ,"formatter": "LevelFormatter" #"info"
            ,"filters": ["require_debug_false"]
        },
        "debug_handler_file": {
            "level": logging.DEBUG
            ,"class":"logging.FileHandler"
            ,"filename": f"{LOG_DIR}/debug.log"
            ,"formatter": "LevelFormatter" #"debug"
            ,"filters": ["require_debug_true", "debug_filter"]
        },
        "info_handler_file": {
            "level": logging.INFO
            ,"class":"logging.FileHandler"
            ,"filename":f"{LOG_DIR}/info.log"
            ,"formatter": "LevelFormatter" #"info"
            ,"filters": ["info_filter"]            
        },
        "warnings_handler_file": {
            "level": logging.WARNING
            ,"class":"logging.FileHandler"
            ,"filename":f"{LOG_DIR}/warnings.log"
            ,"mode": 'a'
            ,"formatter": "LevelFormatter" #"warning"
            ,"filters": ["warning_filter"]
        },
        "errors_handler_file": {
            "level": logging.ERROR
            ,"class":"logging.FileHandler"
            ,"filename":f"{LOG_DIR}/errors.log"
            ,"mode": 'a'
            ,"formatter": "LevelFormatter" #"error"
            ,"filters": ["error_filter"]
        },
        "all_handler_file": {
            "level": logging.NOTSET
            ,"class": "logging.handlers.RotatingFileHandler"
            ,"filename": f"{LOG_DIR}/all_messages.log"
            ,"mode": 'a'
            ,"formatter": "LevelFormatter"
            ,"maxBytes": 1048576
            ,"backupCount": 10
        } 
   
    }, 
    
    # LOGGERS ========================================================
    "loggers": {
        '': {  # root logger
            "handlers" : [
                "debug_handler_console",
                "info_handler_console",
                "debug_handler_file",
                "info_handler_file",
                "warnings_handler_file",
                "errors_handler_file",
                "all_handler_file"
            ],
            "level": logging.DEBUG,
            'propagate': False
        },
        APP_NAME: {
            "handlers" : [
                "debug_handler_console",
                "info_handler_console",
                "debug_handler_file",
                "info_handler_file",
                "warnings_handler_file",
                "errors_handler_file",
                "all_handler_file"
            ],
            "level": logging.DEBUG,
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': [
                "debug_handler_console",
                "info_handler_console",
                "debug_handler_file",
                "info_handler_file",
                "warnings_handler_file",
                "errors_handler_file",
                "all_handler_file"                
            ],
            'level': 'DEBUG',
            'propagate': False
        },        
        'test': { 
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        
        
        "external_library": {
            "handlers": ["info_handler_console"],
            "level": logging.INFO,
            "propagate": False            
        }
    }         

}

