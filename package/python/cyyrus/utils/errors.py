import functools
import logging
from typing import Any, Callable, Optional, Type, Union

from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


def error_handler(
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    handler: Optional[Callable[[Exception], Any]] = None,
    logger: Optional[logging.Logger] = logger,
    retries: int = 0,
    default_return: Any = None,
):
    """
    A decorator factory for custom error handling and returning a default value incase of retires get exhausted.

    Args:
        exceptions: Exception or tuple of exceptions to catch.
        handler: Function to handle the caught exception.
        logger: Logger object to use for logging errors.
        retries: Number of times to retry the function before giving up.
        default_return: Value to return if all retries fail.

    Returns:
        Decorator function for error handling.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if logger:
                        # TODO: explore using logger.exception() instead
                        logger.error(
                            f"Error in {func.__name__}. Attempt {attempt + 1} of {retries + 1}"
                        )

                    if handler:
                        handler_result = handler(e)
                        # If the handler returns a value, use it as the final result
                        if handler_result is not None:
                            return handler_result

                    # If we've reached the last attempt, return the default
                    if attempt == retries:
                        return default_return

            # This line should never be reached, but it's here for completeness
            return default_return

        return wrapper

    return decorator
