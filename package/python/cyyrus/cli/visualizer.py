import pandas as pd
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from cyyrus.models.dataset import Dataset
from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)


class Visualizer:

    @staticmethod
    def display_dataframe_properties(
        df: pd.DataFrame,
    ):
        """
        Display a concise overview of DataFrame properties and optionally visualize data distributions.

        Args:
        df (pd.DataFrame): The input DataFrame.
        logger: Optional logger object for additional logging.
        visualize (bool): Whether to create and display visualizations. Default is True.
        max_categories (int): Maximum number of categories to display for categorical columns. Default is 5.
        """

        console = Console()

        # Basic DataFrame info
        console.print(Panel.fit("[bold blue]DataFrame Overview", style="cyan"))
        console.print(
            f"Shape: [green]{df.shape[0]}[/green] rows, [green]{df.shape[1]}[/green] columns"
        )
        console.print(
            f"Memory usage: [yellow]{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB[/yellow]"
        )

        # Column info
        column_table = Table(title="Column Information", box=box.ROUNDED)
        column_table.add_column("Column Name", style="cyan", no_wrap=True)
        column_table.add_column("Data Type", style="magenta")
        column_table.add_column("Non-Null Count", justify="right", style="green")
        column_table.add_column("Null Count", justify="right", style="red")

        for col in df.columns:
            non_null_count = df[col].count()
            null_count = df[col].isnull().sum()
            column_table.add_row(
                col,
                str(df[col].dtype),
                str(non_null_count),
                str(null_count),
            )

        console.print(column_table)

        # Data types overview
        dtype_tree = Tree("[bold]Data Types Overview")
        for dtype in df.dtypes.value_counts().index:
            dtype_cols = df.select_dtypes(include=[dtype]).columns
            branch = dtype_tree.add(f"[yellow]{dtype}[/yellow]: {len(dtype_cols)} columns")
            for col in dtype_cols:
                branch.add(f"[cyan]{col}[/cyan]")

        console.print(dtype_tree)

    @staticmethod
    def display_dataset_properties(dataset: Dataset):
        """
        Display properties of a Dataset object in a visually appealing way.

        Args:
        dataset (Dataset): The Dataset object to display.
        """
        console = Console()

        # Dataset Metadata
        console.print(Panel.fit("[bold blue]Dataset Metadata", style="cyan"))
        metadata_table = Table(box=box.ROUNDED)
        metadata_table.add_column("Property", style="cyan")
        metadata_table.add_column("Value", style="yellow")

        metadata_table.add_row("Name", dataset.metadata.name)
        metadata_table.add_row("Description", dataset.metadata.description)
        metadata_table.add_row("Tags", ", ".join(dataset.metadata.tags))
        metadata_table.add_row("License", dataset.metadata.license)
        metadata_table.add_row("Languages", ", ".join(dataset.metadata.languages))

        console.print(metadata_table)

        # Dataset Shuffle
        console.print(Panel.fit("[bold blue]Dataset Shuffle", style="cyan"))
        console.print(f"Seed: [yellow]{dataset.shuffle.seed}[/yellow]")

        # Dataset Splits
        console.print(Panel.fit("[bold blue]Dataset Splits", style="cyan"))
        splits_table = Table(box=box.ROUNDED)
        splits_table.add_column("Split", style="cyan")
        splits_table.add_column("Value", style="yellow")

        splits_table.add_row("Train", str(dataset.splits.train))
        splits_table.add_row("Test", str(dataset.splits.test))
        splits_table.add_row("Seed", str(dataset.splits.seed))

        console.print(splits_table)

        # Dataset Attributes
        console.print(Panel.fit("[bold blue]Dataset Attributes", style="cyan"))
        attributes_tree = Tree("[bold]Attributes")

        attributes_tree.add(
            f"Required Columns: [yellow]{', '.join(dataset.attributes.required_columns) or 'None'}[/yellow]"
        )
        attributes_tree.add(
            f"Unique Columns: [yellow]{', '.join(dataset.attributes.unique_columns) or 'None'}[/yellow]"
        )
        attributes_tree.add(f"Nulls: [yellow]{dataset.attributes.nulls}[/yellow]")
        attributes_tree.add(
            f"Flatten Columns: [yellow]{', '.join(dataset.attributes.flatten_columns) or 'None'}[/yellow]"
        )
        attributes_tree.add(
            f"Exclude Columns: [yellow]{', '.join(dataset.attributes.exclude_columns) or 'None'}[/yellow]"
        )

        console.print(attributes_tree)
