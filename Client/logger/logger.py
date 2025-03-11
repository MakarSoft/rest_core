# ====================================================================
# logger/loggers.py
# ====================================================================

__all__ = ['get_logger']

import logging
from logging import config

from typing import Mapping, Any

from  project.logger.logger_dict_config import LOG_CONFIG

# ====================================================================
# ====================================================================
def dict_config(log_config: Mapping[str, Any] = LOG_CONFIG) -> None:
    '''
    Config logging using a dictionary
    '''

    config.dictConfig(log_config)

# ====================================================================
# ====================================================================
def get_logger(
    name: str,
    log_config: Mapping[str, Any] = LOG_CONFIG
) -> logging.Logger:
    '''
    '''
    config.dictConfig(log_config)
    logger = logging.getLogger(name)

    return logger
