import logging
from logging.handlers import RotatingFileHandler


def create_logger(name, file_path, level=logging.DEBUG):
    """
    Create a logger with a rotating file handler and a console handler

    :param name: the name of the logger
    :param file_path: the path of the log file
    :param level: the level of the logger
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a rotating file handler
    file_handler = RotatingFileHandler(file_path,
                                       maxBytes=10*1024*1024,
                                       backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter with file and line number
    formatter = logging.Formatter('%(asctime)s - %(name)s:%(levelname)s'
                                  ' - %(message)s - [%(filename)s:%(lineno)d]',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # Add the formatter to the handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
