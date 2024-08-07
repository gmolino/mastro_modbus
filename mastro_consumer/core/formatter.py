# -*- coding: utf-8 -*-
import logging


class CustomFormatter(logging.Formatter):
    blue = "\x1b[38;5;39m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    green = "\x1b[;32m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_error = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = "%(asctime)s - %(name)s "
    FORMATS = {
        logging.DEBUG: format + blue + "OUTPUT: " + reset + " %(message)s",
        logging.INFO: format + green + "%(levelname)s: " + reset + " %(message)s",
        logging.WARNING: format + yellow + "%(levelname)s: " + reset + " %(message)s",
        logging.ERROR: red + format_error + reset,
        logging.CRITICAL: bold_red + format_error + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())

        self.logger.addHandler(ch)

    def info(self, msg):
        return self.logger.info(msg)

    def warning(self, msg):
        return self.logger.warning(msg)

    def error(self, msg):
        return self.logger.error(msg)
    
    def critical(self, msg):
        return self.logger.critical(msg)
    
    def debug(self, msg):
        return self.logger.debug(msg)
