# package/python/cli/main.py
import logging
import os
from pathlib import Path

import click
import litellm

from cyyrus.cli.utils import create_export_filepath, get_ascii_art
from cyyrus.composer.core import Composer
from cyyrus.composer.dataframe import ExportFormat
from cyyrus.composer.utils import FunnyBones
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
@click.option(
    "--export-format",
    type=click.Choice([format.value for format in ExportFormat]),
    default=None,
    help="Format to export the dataset",
)
@click.option(
    "--export-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory to export the dataset",
)
def run(
    log_level,
    human_readable,
    log_file,
    log_dir,
    schema_path,
    env_path,
    export_format,
    export_path,
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
    # "This is embarassing. Do you want to try exporting again? Maybe with a different format or path?"
    # Export skipped. Maybe next time!
    # Ask if they want to export the dataset
    # Export handling
    if click.confirm("Do you want to export the dataset?"):
        while True:
            if export_path is None:
                export_path = click.prompt(
                    "Enter the export directory",
                    type=click.Path(path_type=Path),
                    default=Path.cwd(),
                )

            if export_format is None:
                export_format = click.prompt(
                    "Enter the export format",
                    type=click.Choice([format.value for format in ExportFormat]),
                    default=ExportFormat.HUGGINGFACE.value,
                )

            suggested_name = FunnyBones.suggest()
            dataset_name = click.prompt(
                f"Enter a name for your dataset (How about: {suggested_name} ?)",
                default=suggested_name,
            )

            full_export_path = create_export_filepath(
                Path(export_path),
                dataset_name,
                export_format,
            )

            if full_export_path.exists():
                if not click.confirm(f"File {full_export_path} already exists. Overwrite?"):
                    export_path = None
                    export_format = None
                    continue

            try:
                composer.export(export_format=export_format, filepath=full_export_path)
                logger.info(
                    f"Exported dataset to {export_path} in {export_format} format. It's now officially your data!"
                )
                break  # Exit the function if export is successful
            except Exception as e:
                logger.error(f"Export failed due to: {str(e)}")
                if not click.confirm(
                    "Do you want to try exporting again with a different format or path?"
                ):
                    logger.info("Skipping export. Moving on!")
                    break  # Exit the function if user doesn't want to try again
                # If user wants to try again, reset format and path to prompt user again
                export_format = None
                export_path = None
    else:
        logger.info("Skipping export. That's cool too! Adieu!")

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
        logger.info(f"Published dataset to {dataset_identifier}. Happy sharing!")
    else:
        logger.info("Publishing skipped. Your data, your rules!")
        return


if __name__ == "__main__":
    cli()
