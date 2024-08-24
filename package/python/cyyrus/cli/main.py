# package/python/cli/main.py
import logging
import os
from pathlib import Path

import click
import litellm

from cyyrus.cli.utils import get_ascii_art
from cyyrus.composer.core import Composer
from cyyrus.models.spec import load_spec
from cyyrus.utils.logging import get_logger, setup_logging


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
@click.option(
    "--schema-path",
    type=click.Path(exists=True),
    required=True,
    help="Path to the schema file",
)
@click.option(
    "--env-path",
    type=click.Path(exists=True),
    help="Path to the optional environment file",
)
def run(
    log_level,
    human_readable,
    log_file,
    log_dir,
    schema_path,
    env_path,
):
    setup_logging(
        log_level=getattr(logging, log_level.upper()),
        log_file=str(log_file),
        for_human=human_readable,
    )
    logger = get_logger(__name__)

    # Start the CLI
    print(get_ascii_art())
    logger.info("CLI started. Buckle up, it's going to be a wild wild ride!")

    if log_dir:
        logger.debug(f"Log directory: {log_dir}")
        log_file = Path(log_dir) / log_file

    logger.debug(f"liteLLM logging level set to {log_level}")
    os.environ["LITELLM_LOG"] = log_level

    litellm_verbosity = False  # log_level == "DEBUG"
    litellm.set_verbose = litellm_verbosity
    logger.debug(f"liteLLM verbose mode set to {litellm_verbosity}")

    # Load the spec
    spec = load_spec(schema_path, env_path)
    logger.info("Spec loaded. Ready to roll!")

    # Initialize the Composer
    composer = Composer(spec=spec)

    # Ask if they want to perform a dry run
    if click.confirm("Do you want to perform a dry run?", default=True):
        composer.compose(dry_run=True)
        logger.info("Dry run complete. Nothing exploded, good start!")
    else:
        logger.info("Skipping dry run. Brave choice")

    # Ask if they want to perform a full run
    if click.confirm("Do you want to perform a full run?", default=True):
        composer.compose()
        logger.info("Full run executed. Hope you liked it!")
    else:
        logger.info("Skipping full run. Until next time!")
        return

    # Display sample dataframe

    df = composer.dataframe
    click.echo("Sample dataframe:")
    click.echo(df.head())
    logger.info("Here's a sneak peek of your data. Doesn't it look fabulous?")

    # Ask if they want to export the dataset
    if click.confirm("Do you want to export the dataset?"):
        export_path = click.prompt(
            "Enter the export path",
            type=click.Path(path_type=Path),
        )
        export_format = click.prompt(
            "Enter the export format",
            type=click.Choice(["json", "parquet", "csv"]),
            default="json",
        )
        composer.export()
        logger.info(
            f"Exported dataset to {export_path}.{export_format}. It's now officially your data!"
        )
    else:
        logger.info("Skipping export. That's cool too! Adieu!")
        return

    # Ask if they want to publish the exported dataset
    if click.confirm("Do you want to publish the dataset?"):
        _ = click.prompt(
            "Enter the huggingface token",
            type=str,
        )
        dataset_identifier = click.prompt(
            "Enter the dataset identifier",
            type=str,
        )
        composer.export()
        logger.info(f"Published dataset to {dataset_identifier}. Happy sharing!")
    else:
        logger.info("Publishing skipped. Your data, your rules!")
        return


if __name__ == "__main__":
    cli()
