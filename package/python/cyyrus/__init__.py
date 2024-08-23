import logging

from .utils.logging import get_logger, setup_logging

# Set up logging for the entire package
setup_logging(
    log_level=logging.INFO,
    log_file="cyyrus.log",
    for_human=True,
)
logger = get_logger()
