from collections import defaultdict
from pydantic import BaseModel, model_validator
from typing import Any, Dict, List, Set, Tuple, Union
import yaml
import requests
from pathlib import Path
from urllib.parse import urlparse
from cyyrus.errors.schema import (
    ColumnIDNotFoundError,
    ColumnTaskIDNotFoundError,
    ColumnTypeNotFoundError,
    SchemaFileNotFoundError,
    SchemaParsingError,
    TaskCyclicDependencyError,
)
from cyyrus.models.column import Column
from cyyrus.models.dataset import Dataset, SpecVersion
from cyyrus.models.task import Task, TaskType
from cyyrus.models.types import CustomType, DataType
from cyyrus.utils.mermaid import Mermaid


class Spec(BaseModel):
    spec: SpecVersion
    dataset: Dataset
    tasks: Dict[str, Task]
    types: Dict[str, CustomType]
    columns: Dict[str, Column]

    def extract_dag_representation(self) -> Dict[str, List[str]]:
        return {
            column_name: list(column.task_input.keys())
            for column_name, column in self.columns.items()
        }

    @model_validator(mode="after")
    def validate_dag(cls, values):
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
                if has_cycle(node, visited, rec_stack):
                    raise TaskCyclicDependencyError(
                        extra_info={
                            "node": node,
                        }
                    )

        return values

    @model_validator(mode="after")
    def validate_columns_for_orphans(cls, values):
        # Note: duplicates are handled by Pydantic + YAML Parser
        required_columns = set(values.dataset.attributes.required_columns)
        all_column_names = set(values.columns.keys())

        # Check if all required columns exist in either columns or references
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

    def extract_task_info(
        self,
        column_name: str,
    ) -> Tuple[str, TaskType, Dict[str, Union[int, str, float]], Dict[str, str], Union[Any, None]]:
        column = self.columns.get(column_name)

        if not column:
            # If the column is still not found, raise an error
            raise ColumnIDNotFoundError(
                extra_info={
                    "column_name": column_name,
                }
            )

        task = self.tasks.get(column.task_id)
        if not task:
            raise ColumnTaskIDNotFoundError(
                extra_info={
                    "column_name": column_name,
                }
            )

        custom_type: CustomType | None = self.types.get(column.column_type)

        return (
            column_name,
            task.task_type,
            task.task_properties,
            column.task_input,
            custom_type.dynamic_model if custom_type else None,
        )

    def generate_mermaid_graph(
        self,
    ) -> Mermaid:
        dag = self.extract_dag_representation()
        mermaid_code = ["graph LR"]
        for task, dependencies in dag.items():
            for dep in dependencies:
                mermaid_code.append(f"    {dep} --> {task}")
        mermaid_code = "\n".join(mermaid_code)
        return Mermaid(mermaid_code)

    def levels(
        self,
    ):
        # Extract the DAG representation
        dependencies: Dict[str, List[str]] = self.extract_dag_representation()

        for level in level_order_traversal(dependencies):
            yield [self.extract_task_info(node) for node in level]


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


def level_order_traversal(
    dependencies: Dict[str, List[str]],
):
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
