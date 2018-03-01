import logging
import logging.handlers

log_value = True

def log(*args, **kargs):
    """
    """
    if log_value is True:
        print(*args, **kargs)
