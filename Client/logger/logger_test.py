# logger_test.py

import random

from  project.tools.decorators import *

from  project.logger import  * 
from  project.logger.logger import get_logger
from  project.logger.logger_dict_config import LOG_CONFIG

logger = get_logger(__name__,  LOG_CONFIG)

#===============================================================================
# Проверка логирования ....
def logger_test():
    logger.info('---Запуск проверки модуля логирования---')

    @func_debug(logger)
    def test_debug():
        print("TEST")

    test_debug()

    # Список handler-ов ...
    for i, h in enumerate(logger.handlers):
        print(f"{i}: {h.name}")

    print(*LogLevel.choices()[:-1])
    print(*(f"{level}: {LogLevel[level]}" for level in LogLevel.choices() if level != 'notset'))

    for i in range(20):
        level = random.choice(LogLevel.choices()[:-1])
        logger.log(LogLevel[level], log_messages[LogLevel[level]] )
    print()

    logger.info('---Завершение проверки модуля логирования---')
