# package/python/cli/main.py
import logging
from pathlib import Path

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(
        [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]
    ),
    help="Set the logging level",
)
@click.option(
    "--human-readable",
    is_flag=True,
    default=True,
    help="Use human-readable log format (default: True)",
)
@click.option(
    "--log-file",
    default="cyyrus.log",
    help="Name of the log file",
)
@click.option(
    "--log-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory to store log files",
)
def run(
    log_level,
    human_readable,
    log_file,
    log_dir,
):
    from package.python.cyyrus.utils.logging import get_logger, setup_logging

    if log_dir:
        log_file = Path(log_dir) / log_file

    setup_logging(
        log_level=getattr(logging, log_level.upper()),
        log_file=str(log_file),
        for_human=human_readable,
    )
    logger = get_logger(__name__)
    logger.info("CLI started")


if __name__ == "__main__":
    cli()
