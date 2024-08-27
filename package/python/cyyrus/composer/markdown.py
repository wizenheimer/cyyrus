import pandas as pd
from jinja2 import Template

from cyyrus.models.spec import Spec


class MarkdownUtils:
    @staticmethod
    def generate_readme(
        spec: Spec,
        repository_id: str,
        dataframe: pd.DataFrame,
    ) -> str:
        template = Template(MarkdownUtils.get_template_string())
        return template.render(
            spec=spec,
            repository_id=repository_id,
            dataframe=dataframe,
        )

    @staticmethod
    def get_template_string():
        return """
# {{ spec.dataset.metadata.name or "Cyyrus Dataset" }}

{{ spec.dataset.metadata.description or "No description provided." }}

This dataset was generated using [Cyyrus](https://github.com/wizenheimer/cyyrus), an open-source library for creating and managing datasets.

## Using the Dataset

To use this dataset with the Hugging Face `datasets` library:

```python
from datasets import load_dataset

dataset = load_dataset("{{ repository_id or 'cyyrus/cyyrus-dataset' }}")
```

## License

This dataset is licensed under the {{ spec.dataset.metadata.license }} license.

## Tags

{% for tag in spec.dataset.metadata.tags %}
- {{ tag }}
{% endfor %}


## Acknowledgements

This dataset was created using [Cyyrus](https://github.com/wizenheimer/cyyrus), an open-source library for dataset generation and management. If you find yourself using this dataset in your work (and why wouldn't you?), consider giving Cyyrus a little love:

```bibtex
@software{cyyrus,
  title = {Cyyrus: An Open-Source Library for Dataset Generation and Management},
  author = {{cyyrus}},
  url = {https://github.com/wizenheimer/cyyrus},
  year = {2024}
}
```

For any questions or issues related to this dataset, please open an issue on the [Cyyrus GitHub repository](https://github.com/wizenheimer/cyyrus/issues).
"""
