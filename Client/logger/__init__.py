# ==============================================================================
# Пакет логирования 
# -----------------
#
# project/_logger/__init__.py
# ==============================================================================

# ------------------------------------------------------------------------------
# Структура проекта...
# ------------------------------------------------------------------------------
#
# [<Project>]           :: Рабочий каталог проекта
#   │
#   ├── main.py
#   │   ...
#   ├── [config]        :: файлы конфигурации
#   │      │...
#   │      └── ...
#   ├── [ logs ]        :: логи
#   │      │...
#   │      └── ...
#   ├── [ project]      :: код проекта  
#   │      │ 
#  ...    ...
#   │      ├── [config] :: пакет для работы 
#   │      │      │...     с конфигурацией приложения 
#   │      │      └── ...
#   │      ├── [ logger ]          :: пакет логирования
#   │      │   ───┬─────           -------------------- 
#   │      │      ├── __init__.py   <- this file
#   │      │      │...                 --------- 
#   │      │      └── ...
#   │      ├── [ pam ]             :: PAM
#   │      │      │...
#   │      │      └── ...
# #  ...    ...
# ------------------------------------------------------------------------------

import logging
import os
import sys
from pathlib import Path

from datetime import datetime
from typing import Final
from project.config import APP_NAME, WORK_DIR   # APP_DEBUG, 

# Типы, используемые логгером...
from .logger_types  import (
    LogFormatType,
    LogLevel,
    LoggerStyle,
    FormatString,
    DateFormatString
)

from .logger_dict_config import LOG_CONFIG

# Константы, используемые форматтером...
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

#===============================================================================

