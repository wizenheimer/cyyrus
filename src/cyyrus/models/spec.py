from pydantic import BaseModel, model_validator
from typing import Dict
import yaml
import requests
from pathlib import Path
from urllib.parse import urlparse
from cyyrus.errors.schema import (
    ColumnIDNotFoundError,
    ColumnTaskIDNotFoundError,
    ColumnTypeNotFoundError,
    DuplicateColumnIDError,
    SchemaFileNotFoundError,
    SchemaParsingError,
)
from cyyrus.models.column import Column
from cyyrus.models.dataset import Dataset, SpecVersion
from cyyrus.models.reference import Reference
from cyyrus.models.task import Task
from cyyrus.models.types import Type, DataType


class Spec(BaseModel):
    spec: SpecVersion
    dataset: Dataset
    reference: Dict[str, Reference]
    tasks: Dict[str, Task]
    types: Dict[str, Type]
    columns: Dict[str, Column]

    @model_validator(mode="after")
    def validate_columns_and_references(cls, values):
        required_columns = set(values.dataset.attributes.required_columns)
        column_names = set(values.columns.keys())
        reference_names = set(values.reference.keys())

        # Check for duplicates between columns and references
        duplicates = column_names.intersection(reference_names)
        if duplicates:
            raise DuplicateColumnIDError(
                extra_info={
                    "duplicates": str(duplicates),
                },
            )

        # Check if all required columns exist in either columns or references
        all_column_names = column_names.union(reference_names)
        missing_columns = required_columns - all_column_names
        if missing_columns:
            raise ColumnIDNotFoundError(
                extra_info={
                    "missing_columns": str(missing_columns),
                },
            )

        return values

    @model_validator(mode="after")
    def validate_column_types(cls, values):
        types = values.types
        for column_name, column in values.columns.items():
            # if column.column_type not in types and column.column_type not in DataType.__members__:
            if column.column_type not in types and column.column_type not in [
                dt.value for dt in DataType
            ]:
                raise ColumnTypeNotFoundError(
                    extra_info={
                        "column_name": column_name,
                        "column_type": column.column_type,
                    },
                )

        # We don't need to validate reference types here anymore as Pydantic will handle it
        return values

    @model_validator(mode="after")
    def validate_task_ids(cls, values):
        tasks = values.tasks
        for column_name, column in values.columns.items():
            if column.task_id not in tasks:
                raise ColumnTaskIDNotFoundError(
                    extra_info={
                        "column_name": column_name,
                        "task_id": column.task_id,
                    },
                )
        return values


def load_spec(path_or_url: str) -> Spec:
    """
    Load a spec from either a local file path or a URL.
    """
    # Check if the source is a URL
    parsed_url = urlparse(path_or_url)
    if parsed_url.scheme and parsed_url.netloc:
        # It's a URL, so use requests to fetch the content
        response = requests.get(path_or_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        yaml_content = response.text
    elif Path(path_or_url).is_file():
        # It's a local file, so read its content
        with open(path_or_url, "r") as file:
            yaml_content = file.read()
    else:
        raise SchemaFileNotFoundError()

    # Parse the YAML content
    try:
        return Spec(**yaml.safe_load(yaml_content))
    except yaml.YAMLError as e:
        raise SchemaParsingError(extra_info={"error": str(e)})
