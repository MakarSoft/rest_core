# ====================================================================
# Настройка фильтров
# 
# project/logger/filters.py
# ====================================================================


__all__ = [
    "DebugOnly",
    "InfoOnly",
    "WarningsOnly",
    "ErrorsOnly",
    "RequireDebugTrue",
    "RequireDebugFalse"
]

import logging

# from . import APP_DEBUG
from project.config import APP_NAME, APP_DEBUG
# APP_DEBUG = True

class DebugOnly(logging.Filter):
    '''
    Обрабатываются все log-events, которые имеют уровень DEBUG и ниже
    '''

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.DEBUG   # <=10


class InfoOnly(logging.Filter):
    '''
    Обрабатываются все log-events, которые имеют уровень от DEBUG до WARNING (не включая)
    '''
    
    def filter(self, record: logging.LogRecord) -> bool:
        return logging.DEBUG < record.levelno < logging.WARNING  #(10..30)


class WarningsOnly(logging.Filter):
    '''
    Обрабатываются все log-events, которые имеют уровень от INFO до ERROR (не включая)
    '''
    
    def filter(self, record: logging.LogRecord) -> bool:
        return logging.INFO < record.levelno < logging.ERROR  #(20..40)


class ErrorsOnly(logging.Filter):
    '''
    Обрабатываются все log-events, которые имеют уровень от WARNING до CRITICAL (не включая)
    '''    
    
    def filter(self, record: logging.LogRecord) -> bool:
        return logging.WARNING < record.levelno < logging.CRITICAL # (30..50)


class RequireDebugFalse(logging.Filter):
    """
    Обрабатываются все log-events, when APP_DEBUG is False
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        return not APP_DEBUG
## ...или вместо класса
# def require_debug_false():
#     """
#     Обрабатываются все log-events, when APP_DEBUG is False
#     """
#
#     def filter(record):
#         return not APP_DEBUG
#     return filter


class RequireDebugTrue(logging.Filter):
    """
    Обрабатываются все log-events, when DEBUG is True
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return APP_DEBUG
## ...или вместо класса
# def require_debug_true():
#     """Обрабатываются все log-events, when APP_DEBUG is True"""
#     def filter(record):
#         return APP_DEBUG
#     return filter

