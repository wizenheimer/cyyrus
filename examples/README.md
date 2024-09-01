# Examples

This directory contains schema examples and a Jupyter notebook to help you get started with Cyyrus.

## Directory Structure

```
examples
├── README.md
├── notebook
│   └── schema_cookbook.ipynb
└── schema
    ├── graph_parsing.yaml
    ├── invoice_parsing.yaml
    ├── movie_review.yaml
    └── ocr_free_markdown.yaml
```

## Contents

### Notebook

- `notebook/schema_cookbook.ipynb`: Notebook for creating and configuring schemas for Cyyrus. Or try out [![Schema Cookbook](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/18qYnYKPHiCWRqH92bzpNujJoC4dYqWS-?usp=sharing)

### Schema Examples

- `schema/extract_info_from_invoice.yaml`: Example schema for extracting customer data, invoice data from invoices and synthesizing new data.
- `schema/generate_product_review.yaml`: Schema setup for generating and rating product reviews.
- `schema/annual_report_to_markdown.yaml`: Example schema for converting Annual report to Markdown without using OCR.

## Getting Started

1. Clone this repository.
2. Explore the `schema` directory for YAML configuration examples.
3. Open `schema_cookbook.ipynb` in Jupyter to interactively create and modify schemas.

For detailed documentation and usage instructions, visit our [main documentation](https://cyyrus.com).

## Contributing

Feel free to contribute your own examples by submitting a pull request!

## Support

If you have any questions or run into issues, please [open an issue](https://github.com/wizenheimer/cyyrus/issues/new/choose) on our GitHub repository.