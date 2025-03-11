# ====================================================================
# 
#
# projectt/logger/app_loger.py
# ====================================================================
import logging
import sys
from typing import Optional

from . import (
    LOG_FORMAT,
    LogFormatType,
    LogLevel,
    LoggerStyle,
    FormatString
)

class AppLogger:
    """
    Basic application logger class
    """

    name = 'AppLogger'

    format_config = LOG_FORMAT[LogFormatType.LOG_MEDIUM]['%']
    alt_format_config= LOG_FORMAT[LogFormatType.LOG_LONG]['%']
    msg_format_config = '%(message)s'
    time_config = '%H:%M:%S'

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __init__(
        self,
        name: str,
        level: int = logging.DEBUG,
        stream: bool = True,
        file: Optional[str] = None
    ) -> None:
        
        self.name = name
        self.level = level
        self.stream = stream
        self.file = file
        self.debug_formatter = logging.Formatter(self.format_config, self.time_config)
        self.alt_formatter = logging.Formatter(self.alt_format_config)
        self.msg_formatter = logging.Formatter(self.msg_format_config)
        self.applogger = None
        self.stream_handler = None
        self.file_handler = None

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def create(self) -> logging.Logger:

        self.applogger = logging.getLogger(self.name)
        
        self.applogger.setLevel(self.level)
        
        if self.stream:
            self.stream_handler = self.add_stream_handler()
        if self.file:
            self.file_handler = self.add_file_handler()
        
        self.add_custom_methods()
        
        return self.applogger
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def add_file_handler(self):

        from logging import handlers
        file_handler = handlers.RotatingFileHandler(
            self.file,
            maxBytes=1024*1024,
            backupCount=5
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(self.alt_formatter)

        self.applogger.addHandler(file_handler)
        
        return file_handler

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def add_stream_handler(self):

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(self.debug_formatter)

        self.applogger.addHandler(stream_handler)

        return stream_handler

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def add_custom_methods(self) -> None:
        
        method_list = [
            self.handle_uncaught_system_exception,
            self.get_stack,
            self.write_to_level,
            self.inspect_dict,
            self.inspect_obj
        ]
        for item in method_list:
            setattr(self.applogger, item.__name__, item)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def handle_uncaught_system_exception(
        self,
        exc_type,
        exc_value,
        exc_traceback
    ) -> None:
        # см. sys.exc_info(), sys.exceptiot()
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
    
        print('[UNCAUGHT SYSTEM EXCEPTION]')
        self.applogger.critical("UNCAUGHT EXCEPTION", exc_info=(exc_type, exc_value, exc_traceback), stack_info=True)
        print('[/UNCAUGHT SYSTEM EXCEPTION]')
        sys.exit()


    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def get_stack(
        self,
        msg: str,
        level: LogLevel = logging.DEBUG
    ):
        self.applogger.log(self.level, msg, stack_info=True)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def write_to_level(
        self,
        level: LogLevel,
        log_string: str
    ) -> None:

        self.applogger.log(level, log_string)
        
        # self.applogger.debug(log_string)
        # self.applogger.info(log_string)
        # self.applogger.error(log_string)
        # self.applogger.warning(log_string)
        # self.applogger.critical(log_string)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def inspect_obj(self, obj, level=logging.DEBUG):
        """
        Log basic info on obj
        """
        parameters = (id(obj), type(obj), len(obj), sys.getsizeof(obj), obj, sys._getframe().f_back.f_code.co_name)

        log_string = \
            "***** Object Info *****\n"\
            "\t   id: {}\n"\
            "\t   type: {}\n"\
            "\t   len: {}\n"\
            "\t   size: {}\n"\
            "\t   self: {}\n"\
            "\t   caller: {}\n"\

        log_string = log_string.format(*parameters)
        self.write_to_level(level, log_string)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def inspect_dict(self, d, level=logging.DEBUG):
        """
        Log basic info on dictionary d.
        :param d: dictionary to display
        :param level: to log
        """
        if not isinstance(d, type({})):
            self.write_to_level('error', "LogError: {} is not a dict.".format(d))
            return

        log_string = ''
        # Header
        log_string += "***** Dictionary Info *****\n"
        # Num keys
        log_string += "\t   Num Keys: {}\n".format(len(d.keys()))
        # Secondary Header
        log_string += "\t   *** Key/Val Pairs ***\n"
        # Key val pairs
        for item in d:
            current = "\t   {}: {}\n".format(item,  d[item])
            log_string += current

        self.write_to_level(level, log_string)

