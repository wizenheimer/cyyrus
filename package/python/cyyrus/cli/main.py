# package/python/cli/main.py
import logging
import os
from pathlib import Path
from typing import Optional

import click
from pandas import DataFrame

from cyyrus.cli.utils import create_export_filepath, get_ascii_art
from cyyrus.cli.visualizer import Visualizer
from cyyrus.composer.core import Composer
from cyyrus.composer.dataframe import ExportFormat
from cyyrus.composer.utils import FunnyBones
from cyyrus.models.spec import Spec, load_spec
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
@click.option(
    "--huggingface-token",
    type=str,
    default=None,
    help="Hugging Face token",
)
@click.option(
    "--repo-id",
    type=str,
    default=None,
    help="Hugging Face repo ID",
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
    huggingface_token,
    repo_id,
):
    # ============================
    #       Setup logging
    # ============================
    if log_dir:
        log_file = Path(log_dir) / log_file

    setup_logging(
        log_level=getattr(logging, log_level.upper()),
        log_file=str(log_file),
        log_dir=log_dir,
        for_human=human_readable,
    )
    logger = get_logger(__name__)

    # ============================
    #      Prepare the CLI
    # ============================
    print(get_ascii_art())
    logger.info("CLI started. Buckle up, it's going to be a wild wild ride!")

    configure_hf()

    # ============================
    #      Load the spec
    # ============================
    spec = load_spec(schema_path, env_path)
    logger.info("Spec loaded. Ready to roll!")

    # ============================
    #      Initialize the composer
    # ============================
    composer = Composer(spec=spec)

    # ============================
    #      Perform the dry run
    # ============================
    if perform_dry_run():
        composer.compose(dry_run=True)
        logger.info("Dry run complete. Nothing exploded, good start!")
    else:
        logger.info("Skipping dry run. Brave choice")

    # ========================================================
    #      Perform the full run and display the sample dataframe
    # ========================================================
    if perform_full_run():
        composer.compose()
        logger.info("Full run executed. Hope you liked it!")
    else:
        logger.info("Skipping full run. Until next time!")
        return

    display_intermediate_results(
        composer.dataframe,
        spec,
        logger,
    )

    # ============================
    #      Export the dataset
    # ============================
    if export_dataset(
        composer=composer,
        export_path=export_path,
        export_format=export_format,
        logger=logger,
    ):
        if publish_dataset(
            composer=composer,
            huggingface_token=huggingface_token,
            repo_id=repo_id,
            logger=logger,
            export_path=export_path,
            export_format=export_format,
        ):
            logger.info("Dataset published successfully!")
        else:
            logger.info("Dataset publishing skipped or failed.")
    else:
        logger.info("Dataset export skipped.")


def configure_hf():
    os.environ["HF_HUB_DISABLE_EXPERIMENTAL_WARNING"] = "1"


def perform_dry_run():
    return click.confirm("Do you want to perform a dry run?", default=True)


def perform_full_run():
    return click.confirm("Do you want to perform a full run?", default=True)


def display_intermediate_results(
    df: DataFrame,
    spec: Spec,
    logger,
):
    logger.info("Here's a sneak peek of your data. Doesn't it look fabulous?")
    Visualizer.display_dataframe_properties(
        df,
    )
    Visualizer.display_dataset_properties(
        spec.dataset,
    )


def export_dataset(
    composer: Composer,
    export_path: Path,
    export_format: ExportFormat,
    logger: logging.Logger,
):
    if not click.confirm("Ready to export the dataset?"):
        return False

    while True:
        export_path, export_format, dataset_name = prompt_export_details(
            export_path,
            export_format,
        )
        full_export_path = create_export_filepath(
            Path(export_path),
            dataset_name,
            export_format,
        )

        if full_export_path.exists() and not click.confirm(
            f"File {full_export_path} already exists. Overwrite?"
        ):
            continue

        try:
            composer.export(export_format=export_format, filepath=full_export_path)
            logger.info(
                f"Exported dataset to {export_path} in {export_format} format. It's now officially your data!"
            )
            return True
        except Exception as e:
            logger.error(f"Export failed due to: {str(e)}")
            if not click.confirm(
                "Do you want to try exporting again with a different format or path?"
            ):
                logger.info("Skipping export. Moving on!")
                return False


def prompt_export_details(export_path, export_format):
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

    return export_path, export_format, dataset_name


def publish_dataset(
    composer: Composer,
    logger: logging.Logger,
    export_path: Path,
    export_format: ExportFormat,
    huggingface_token: Optional[str] = None,
    repo_id: Optional[str] = None,
):
    if not click.confirm("Do you want to publish the dataset?"):
        return False

    hf_token = get_huggingface_token(huggingface_token)
    repository_id: str = (
        click.prompt("Enter the repository identifier", type=str) if repo_id is None else repo_id
    )
    is_private = click.confirm("Keep the dataset private?", default=False)

    try:
        composer.publish(
            repository_id=repository_id,
            huggingface_token=hf_token,
            private=is_private,
        )
        logger.info(f"Published dataset to {repo_id}. Happy sharing!")
        return True
    except Exception as e:
        logger.error(f"Publishing failed due to: {str(e)}")
        if click.confirm("Do you want to retry publishing?"):
            try:
                composer.publish(
                    repository_id=repository_id,
                    huggingface_token=hf_token,
                    private=is_private,
                )
                logger.info(f"Published dataset to {repo_id}. Happy sharing!")
                return True
            except Exception as e:
                logger.error(f"Publishing failed again due to: {str(e)}")
                return (
                    export_dataset(
                        composer=composer,
                        logger=logger,
                        export_format=export_format,
                        export_path=export_path,
                    )
                    if click.confirm("Do you want to export the dataset locally instead?")
                    else False
                )
        return False


def get_huggingface_token(huggingface_token):
    if huggingface_token:
        return huggingface_token

    hf_token = os.environ.get("HF_TOKEN")
    if hf_token and click.confirm(
        f"HF_TOKEN found in environment. Use '{hf_token[:5]}...{hf_token[-5:]}'?"
    ):
        return hf_token

    return click.prompt("Enter the Hugging Face token", type=str, hide_input=True)


def handle_publishing_error(composer, error, repo_id, hf_token, is_private, logger):
    logger.error(f"Publishing failed due to: {str(error)}")
    if click.confirm("Do you want to retry publishing?"):
        try:
            composer.publish(repo_id=repo_id, huggingface_token=hf_token, private=is_private)
            logger.info(f"Published dataset to {repo_id}. Happy sharing!")
            return True
        except Exception as e:
            logger.error(f"Publishing failed again due to: {str(e)}")
            return (
                handle_local_export(composer, logger)
                if click.confirm("Do you want to export the dataset locally instead?")
                else False
            )
    return False


def handle_local_export(composer, logger):
    export_path = click.prompt(
        "Enter the export directory",
        type=click.Path(path_type=Path),
        default=Path.cwd(),
    )
    export_format = click.prompt(
        "Enter the export format",
        type=click.Choice([format.value for format in ExportFormat]),
        default=ExportFormat.HUGGINGFACE.value,
    )
    full_export_path = create_export_filepath(
        Path(export_path),
        click.prompt("Enter a name for your dataset", type=str),
        export_format,
    )
    composer.export(export_format=export_format, filepath=full_export_path)
    logger.info(f"Exported dataset to {full_export_path} in {export_format} format.")
    return True


if __name__ == "__main__":
    cli()
