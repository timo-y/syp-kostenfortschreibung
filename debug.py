"""
#
#   DEBUG
#   Decorators and functions to debug.
#
"""
import time
import functools
import logging

"""
#
#   LOGGING DECORATOR
#
#
"""


def log(func):
    level = logging.DEBUG

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.log(level, f">> starting {func.__name__} with args: {args} - {kwargs}")
        output = func(*args, **kwargs)
        logger.log(level, f"|| completed {func.__name__} returned: {output}")
        return output

    return wrapper


def log_info(func):
    level = logging.INFO

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.log(level, f">> starting {func.__name__} with args: {args} - {kwargs}")
        output = func(*args, **kwargs)
        logger.log(level, f"|| completed {func.__name__} returned: {output}")
        return output

    return wrapper


def log_warning(func):
    level = logging.WARNING

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.log(level, f"starting {func.__name__} with args: {args} - {kwargs}")
        output = func(*args, **kwargs)
        logger.log(level, f"completed {func.__name__} returned: {output}")
        return output

    return wrapper


def log_error(func):
    level = logging.ERROR

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.log(level, f"starting {func.__name__} with args: {args} - {kwargs}")
        output = func(*args, **kwargs)
        logger.log(level, f"completed {func.__name__} returned: {output}")
        return output

    return wrapper


"""
#
#   LOGGING MESSAGE
#
#
"""


def debug_msg(msg):
    level = logging.DEBUG
    logging.log(level, msg)


def info_msg(msg):
    level = logging.INFO
    logging.log(level, msg)


def warning_msg(msg):
    level = logging.WARNING
    logging.log(level, msg)


def error_msg(msg):
    level = logging.ERROR
    logging.log(level, msg)


"""
#
#   TIME FUNCTIONS DECORATOR
#
#
"""


def timeit(func):
    @functools.wraps(
        func
    )  # activate to preserve information (needs to have functools imported,  i.e. import functools)
    def wrapper(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        print("%r  %2.2f ms" % (func.__name__, (te - ts) * 1000))
        return result

    return wrapper
