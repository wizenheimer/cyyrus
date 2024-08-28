import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, Generator, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

import requests
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, model_validator
from pydantic.fields import Field

from cyyrus.constants.messages import Messages
from cyyrus.models.column import Column
from cyyrus.models.dataset import Dataset, SpecVersion
from cyyrus.models.task import Task, TaskType
from cyyrus.models.types import CustomType, TypeMappingUtils
from cyyrus.utils.logging import get_logger
from cyyrus.utils.mermaid import Mermaid

logger = get_logger(__name__)


class Spec(BaseModel):
    spec: SpecVersion
    dataset: Dataset
    tasks: Dict[str, Task]
    types: Optional[Dict[str, CustomType]] = Field(
        default=None,
        exclude=True,
    )
    columns: Dict[str, Column]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._populate_concrete_model()

    def _populate_concrete_model(
        self,
    ):
        """
        Create a concrete model for the response_format specified in the task properties.
        """
        logger.debug("Attempting to populate concrete model for response_format")
        # Create a defaultdict that returns None for missing keys
        custom_types: DefaultDict[str, Optional[Dict[str, Any]]] = defaultdict(lambda: None)

        # Extract the custom types
        # Populate the defaultdict with the custom types
        if self.types:
            for type_name, custom_type in self.types.items():
                custom_types[type_name] = custom_type.model_dump()

        # Update the task properties with the concrete model, incase response_format is specified
        for task_id, task in self.tasks.items():
            # Check if the task is of type generation
            if task.task_type == TaskType.GENERATION:
                # Get the response_format_identifier
                response_format_identifier = task.task_properties.get(
                    "response_format",
                    None,
                )

                # Skip if response_format is not specified
                if not response_format_identifier:
                    continue

                # Get the concrete model for the response_format
                concrete_type_def = custom_types.get(
                    response_format_identifier,
                )
                concrete_model = TypeMappingUtils.get_concrete_model(
                    concrete_type_def,
                )
                task.task_properties["response_format"] = concrete_model
                logger.debug(
                    f"Populated concrete model for response_format {response_format_identifier}"
                )

                # Update the column properties with the concrete model
                self.tasks[task_id] = task
                logger.debug(f"Updated task {task_id} with concrete model")

        logger.debug("Populated concrete models for response_format")

    def extract_dag_representation(
        self,
    ) -> Dict[
        str,
        List[str],
    ]:
        """
        Extract the DAG representation of the spec.
        """
        return {
            column_name: list(column.task_input) for column_name, column in self.columns.items()
        }

    @model_validator(mode="after")
    def validate_dag(
        cls,
        values,
    ):
        """
        Validate the DAG representation of the spec.
        """
        logger.debug("Validating the DAG representation of the spec")
        dag = values.extract_dag_representation()

        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in dag.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        for node in dag:
            if node not in visited:
                logger.debug(f"Checking for cycle starting at `{node}` node")
                if has_cycle(node, visited, rec_stack):
                    logger.error(f"{Messages.TASK_INPUTS_CYCLIC_DEPENDENCY}: {node}")
                    raise ValueError(Messages.TASK_INPUTS_CYCLIC_DEPENDENCY)

        logger.debug("DAG representation is valid")
        return values

    @model_validator(mode="after")
    def validate_columns_for_orphans(
        cls,
        values,
    ):
        """
        Validate that all columns have a task associated with them.
        """
        logger.debug("Validating columns for orphans")
        # Note: duplicates are handled by Pydantic + YAML Parser
        all_column_names = set(values.columns.keys())

        # Check if all required columns exist in either columns or references
        required_columns = set(values.dataset.attributes.required_columns)
        missing_columns = required_columns - all_column_names
        if missing_columns:
            logger.error(f"{Messages.REQUIRED_COLUMN_MISSING} columns: {missing_columns}")
            raise ValueError(Messages.REQUIRED_COLUMN_MISSING)

        # Check if all flatten columns exist in either columns or references
        flatten_columns = set(values.dataset.attributes.flatten_columns)
        missing_columns = flatten_columns - all_column_names
        if missing_columns:
            logger.error(f"{Messages.REQUIRED_COLUMN_MISSING} columns: {missing_columns}")
            raise ValueError(Messages.REQUIRED_COLUMN_MISSING)

        # Check if all unique columns exist in either columns or references
        unique_columns = set(values.dataset.attributes.unique_columns)
        missing_columns = unique_columns - all_column_names
        if missing_columns:
            logger.error(f"{Messages.REQUIRED_COLUMN_MISSING} columns: {missing_columns}")
            raise ValueError(Messages.REQUIRED_COLUMN_MISSING)

        # Check if all exclude columns exist in either columns or references
        excluded_columns = set(values.dataset.attributes.exclude_columns)
        missing_columns = excluded_columns - all_column_names
        if missing_columns:
            logger.error(f"{Messages.REQUIRED_COLUMN_MISSING} columns: {missing_columns}")
            raise ValueError(Messages.REQUIRED_COLUMN_MISSING)

        logger.debug("Columns are valid")
        return values

    @model_validator(mode="after")
    def validate_task_ids(
        cls,
        values,
    ):
        """
        Validate that all columns have a valid task_id associated with them.
        """
        logger.debug("Validating task IDs")
        tasks = values.tasks
        for column_name, column in values.columns.items():
            if column.task_id not in tasks:
                logger.error(
                    f"{Messages.COLUMN_TASK_ID_NOT_FOUND}: {column.task_id} for {column_name}"
                )
                raise ValueError(Messages.COLUMN_TASK_ID_NOT_FOUND)
        logger.debug("Task IDs are validated")
        return values

    def extract_task_info(
        self,
        column_name: str,
    ) -> Tuple[
        List[str],
        str,
        TaskType,
        Dict[str, Union[int, str, float]],
    ]:
        """
        Extract the task information for a given column.
        """
        column = self.columns.get(column_name)

        if not column:
            # If the column is still not found, raise an error
            logger.error(f"{Messages.COLUMNN_ID_NOT_FOUND}: {column_name}")
            raise ValueError(Messages.COLUMNN_ID_NOT_FOUND)

        task = self.tasks.get(column.task_id)
        if not task:
            logger.error(f"{Messages.COLUMN_TASK_ID_NOT_FOUND}: {column_name}")
            raise ValueError(Messages.COLUMN_TASK_ID_NOT_FOUND)

        return (
            # Column Information
            column.task_input,
            column_name,
            # Task Information
            task.task_type,
            task.task_properties,
        )

    def to_dict(
        self,
        *args,
        **kwargs,
    ):
        """
        Convert the Spec object to a dictionary.
        """
        return super().model_dump(*args, **kwargs)

    def preview(
        self,
    ) -> Mermaid:
        """
        Generate a Mermaid graph representation of the DAG.
        """
        logger.debug("Generating a Mermaid graph representation of the DAG")
        dag = self.extract_dag_representation()
        mermaid_code = ["graph LR"]
        for task, dependencies in dag.items():
            for dep in dependencies:
                mermaid_code.append(f"    {dep} --> {task}")
        mermaid_code = "\n".join(mermaid_code)
        return Mermaid(mermaid_code)

    def levels(
        self,
    ) -> Generator[
        List[
            Tuple[
                List[str],
                str,
                TaskType,
                Dict[str, Any],
            ]
        ],
        None,
        None,
    ]:
        """
        Generate the levels of the DAG.
        """
        # Extract the DAG representation
        dependencies: Dict[str, List[str]] = self.extract_dag_representation()

        for level in level_order_traversal(dependencies):
            yield [self.extract_task_info(node) for node in level]


def env_var_constructor(
    loader,
    node,
):
    """
    Custom YAML constructor to replace environment variables.
    """
    value = loader.construct_scalar(node)

    # Handle ${VAR} syntax
    match = re.match(r"\${(.+)}", value)
    if match:
        env_var = match.group(1)
    else:
        # Handle $VAR syntax, allowing for whitespace after $
        env_var = value.strip().lstrip("$").strip()

    # Look up the environment variable, fall back to the original value if not found
    return os.environ.get(env_var, value)


def load_spec(
    path_or_url: str,
    env_file: Optional[str] = None,
):
    """
    Load a spec from either a local file path or a URL, with support for environment variables.
    """
    # Load environment variables from .env file if specified
    if env_file:
        logger.debug(f"Loading environment variables from {env_file}")
        load_dotenv(env_file)

    # Check if the source is a URL
    parsed_url = urlparse(path_or_url)
    if parsed_url.scheme and parsed_url.netloc:
        # It's a URL, so use requests to fetch the content
        try:
            logger.info(f"Fetching spec from {path_or_url}")
            response = requests.get(path_or_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            yaml_content = response.text
        except requests.RequestException as e:
            logger.error(f"{Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED} {path_or_url}: {e}")
            raise ValueError(Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED)
    elif Path(path_or_url).is_file():
        # It's a local file, so read its content
        try:
            logger.info(f"Reading spec from {path_or_url}")
            with open(path_or_url, "r") as file:
                yaml_content = file.read()
        except IOError as e:
            logger.error(f"{Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED} {path_or_url}: {e}")
            raise ValueError(Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED)
    else:
        # The path is neither a URL nor a file
        logger.error(
            f"{Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED} unrecognized path: {path_or_url}"
        )
        raise ValueError(Messages.SCHEMA_FILE_COULD_NOT_BE_LOCATED)

    # Parse the YAML content
    try:
        # Use a custom loader that expands environment variables
        class EnvVarLoader(yaml.SafeLoader):
            pass

        # Add implicit resolver for environment variables
        EnvVarLoader.add_implicit_resolver(
            "env_var",
            re.compile(r"(\$\s*[A-Za-z_][A-Za-z0-9_]*|\$\{[A-Za-z_][A-Za-z0-9_]*\})"),
            first=["$"],
        )

        # Add constructor for environment variables
        EnvVarLoader.add_constructor("env_var", env_var_constructor)

        # Parse the YAML content
        logger.info("Parsing the spec")
        parsed_spec = Spec(**yaml.load(yaml_content, Loader=EnvVarLoader))

        logger.info("Parsed and validated the spec")
        return parsed_spec
    except yaml.YAMLError as e:
        # Raise an error if the YAML parsing fails
        logger.error(f"{Messages.SCHEMA_COULD_NOT_BE_PARSED}: {e}")
        raise ValueError(Messages.SCHEMA_COULD_NOT_BE_PARSED)


def level_order_traversal(
    dependencies: Dict[
        str,
        List[str],
    ],
):
    """
    Perform a level order traversal of the DAG.
    """
    logger.debug("Performing level order traversal of the DAG")
    # Create a reverse dependency graph using defaultdict
    reverse_deps = defaultdict(list)
    all_nodes = set()

    for node, deps in dependencies.items():
        all_nodes.add(node)
        all_nodes.update(deps)
        for dep in deps:
            reverse_deps[dep].append(node)

    # Ensure all nodes are in the dependencies dict
    for node in all_nodes:
        if node not in dependencies:
            dependencies[node] = []

    # Find nodes with no dependencies (root nodes)
    root_nodes = [node for node in all_nodes if not dependencies[node]]

    visited = set()
    current_level = root_nodes

    while current_level:
        current_level = list(dict.fromkeys(current_level))  # Remove duplicates
        visited.update(current_level)
        next_level = []
        for node in current_level:
            for child in reverse_deps[node]:
                if child not in visited and all(dep in visited for dep in dependencies[child]):
                    # Add the child to the next level
                    next_level.append(child)
        # Yield the current level
        yield current_level
        current_level = next_level
