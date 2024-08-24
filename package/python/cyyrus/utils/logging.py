import logging
from functools import lru_cache
from logging import handlers
from pathlib import Path
from typing import Dict, Optional

import colorlog
from pythonjsonlogger import jsonlogger
from tqdm import tqdm

# Default silenced loggers
DEFAULT_SILENCED_LOGGERS = {
    "urllib3": logging.WARNING,
    "requests": logging.WARNING,
    "matplotlib": logging.WARNING,
    "paramiko": logging.WARNING,
    "boto3": logging.WARNING,
    "botocore": logging.WARNING,
    "nose": logging.WARNING,
}


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging(
    log_level=logging.INFO,
    log_file=None,
    for_human=True,
    log_dir: Optional[Path] = None,
    silenced_loggers: Optional[Dict[str, int]] = None,
):
    """
    Set up logging for the application.
    """
    # Use provided log_dir if given, otherwise use default
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent.parent.parent / "logs"

    # Create logs directory if it doesn't exist
    log_dir.mkdir(exist_ok=True)

    # Set up root logger
    root_logger = logging.getLogger("cyyrus")
    root_logger.setLevel(log_level)

    # Create formatters
    if for_human:
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
        )
    else:
        console_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        )
        file_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        )

    # TQDM handler
    console_handler = TqdmLoggingHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = handlers.RotatingFileHandler(
            log_dir / log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Silence chatty libraries
    silenced_loggers = silenced_loggers or DEFAULT_SILENCED_LOGGERS
    for logger_name, level in silenced_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

    return root_logger


@lru_cache()
def get_logger(
    name: Optional[str] = None,
) -> logging.Logger:
    """
    Retrieves a logger with the given name, or the root logger if no name is given.

    Args:
        name: The name of the logger to retrieve.

    Returns:
        The logger with the given name, or the root logger if no name is given.

    Example:
        Basic Usage of `get_logger`
        ```python
        from cyyrus.utils.logging_config import get_logger

        logger = get_logger("cyyrus.test")
        logger.info("This is a test") # Output: cyyrus.test: This is a test

        debug_logger = get_logger("cyyrus.debug")
        debug_logger.debug("Debug message")
        ```
    """
    parent_logger = logging.getLogger("cyyrus")

    if name:
        # Append the name if given but allow explicit full names e.g. "cyyrus.test"
        # should not become "cyyrus.cyyrus.test"
        if not name.startswith(parent_logger.name + "."):
            logger = parent_logger.getChild(name)
        else:
            logger = logging.getLogger(name)
    else:
        logger = parent_logger

    return logger


def deprecated(
    message: str,
    version: str,
):
    """
    Decorator to mark a function as deprecated.

    Args:
        message (str): The deprecation message.
        version (str): The version in which the function is deprecated.

    Returns:
        function: The decorated function.

    Example:
        @deprecated("This function is deprecated", "1.0")
        def my_function():
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            get_logger(__file__).warning(
                f"WARNING: {func.__name__} is deprecated as of version {version}. {message}".strip(),
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# if __name__ == "__main__":
#     setup_logging(
#         log_level=logging.DEBUG,
#         log_file="cyyrus.log",
#         for_human=True,
#     )
#     logger = get_logger("cyyrus.test")
#     logger.debug("This is a debug message")
#     logger.info("This is an info message")
#     logger.warning("This is a warning message")
#     logger.error("This is an error message")
#     logger.critical("This is a critical message")

#     @deprecated("Use new_function instead", "1.0")
#     def old_function():
#         pass

#     old_function()
