"""A logger

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

Created:
    02.01.2022

License identifier:
    GPL-3.0
"""

import logging
from logging.handlers import RotatingFileHandler
from os import listdir, path
import os

from misc.constants import KITREE_CONFIG_DIR

class Logger():
    """Wrapper around Pythons's `logging` module used to initialize and generate loggers.
    """

    @staticmethod
    def Init():
        """Initialize the logging module with the following configuration:
        - Custom formatter
        - Rotating file handler
        - Stream handler to print the log output to the console, if required
        """
        format = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
 
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(format)
        # stream_handler.setFormatter(format)
        # logger.addHandler(stream_handler)

        for file in listdir(KITREE_CONFIG_DIR):
            if "kitree.log" in file:
                os.remove(path.join(KITREE_CONFIG_DIR, file))

        file_handler = RotatingFileHandler(path.join(KITREE_CONFIG_DIR, "kitree.log"), maxBytes = 10e6, backupCount = 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(format)
        logger.addHandler(file_handler)

    @staticmethod
    def Create(name: str):
        """Create a logger with the given name. Normally used with the `__name__` attribute as name
        to have the module name in the log output.
        
        Returns
            Logger: Handle to logger with given name
        """
        return logging.getLogger(name)