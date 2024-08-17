import base64
from typing import Union


class Mermaid:
    """
    This class represents a Mermaid diagram and provides functionality
    to display it in a Jupyter notebook.
    """

    def __init__(self, diagram: str, position: Union[str, None] = None):
        """
        Initialize the Mermaid class with the Mermaid diagram script and optional position.

        Parameters:
            diagram (str): The Mermaid diagram script.
            position (Union[str, None]): The position of the diagram (left, right, center).
        """
        self.position = position
        self.diagram = self._process_diagram(diagram)
        self.svg_url = f"https://mermaid.ink/svg/{self.diagram}"

    def _process_diagram(self, diagram: str) -> str:
        """
        Process the Mermaid diagram script into a base64 encoded string.

        Parameters:
            diagram (str): The Mermaid diagram script.

        Returns:
            str: The base64 encoded string of the Mermaid diagram script.
        """
        graphbytes = diagram.encode("utf8")
        base64_bytes = base64.b64encode(graphbytes)
        return base64_bytes.decode("ascii")

    def _repr_html_(self) -> str:
        """
        Generate HTML to display the Mermaid diagram.

        Returns:
            str: HTML representation of the Mermaid diagram.
        """
        position_style = f"text-align:{self.position};" if self.position else ""
        return f'<div style="{position_style}"><img src="{self.svg_url}" /></div>'


# IPython magic function for easy use in Jupyter notebooks
# try:
#     from IPython.core.magic import register_cell_magic

#     @register_cell_magic
#     def mermaid(line, cell):
#         """
#         IPython cell magic for rendering Mermaid diagrams in Jupyter notebooks.

#         Parameters:
#             line (str): Options for rendering (e.g., --position).
#             cell (str): The Mermaid diagram script.
#         """
#         options = line.strip().split()
#         position = None
#         if "--position" in options:
#             position_index = options.index("--position") + 1
#             if position_index < len(options):
#                 position = options[position_index]
#         diagram = cell.strip()
#         mermaid = Mermaid(diagram, position)
#         display(HTML(mermaid._repr_html_()))

# except ImportError:
#     print("Error occurred while importing IPython modules.")
