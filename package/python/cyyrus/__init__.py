# import logging

from .models.spec import load_spec

# from .utils.logging import get_logger, setup_logging

# Set up logging for the entire package
# setup_logging(
#     log_level=logging.DEBUG,
#     log_file="cyyrus.log",
#     for_human=True,
# )
# logger = get_logger()

__all__ = [
    "load_spec",
]
