# Examples

This directory contains schema examples and a Jupyter notebook to help you get started with Cyyrus.

## Directory Structure

```
examples
├── README.md
├── exports
│   ├── doclaynet_bench
│   │   └── result.jsonl
│   ├── funsd_layoutlmv3
│   │   └── result.jsonl
│   ├── invoices_receipts_ocr_v1
│   │   └── result.jsonl
│   └── layoutlm_resume_data
│       └── result.jsonl
├── notebook
│   └── schema_cookbook.ipynb
└── schema
    ├── annual_report_to_markdown.yaml
    ├── doclaynet_bench.yaml
    ├── extract_info_from_invoice.yaml
    ├── funsd_layoutlmv3.yaml
    ├── generate_product_review.yaml
    ├── graph_parsing.yaml
    ├── invoices_receipts_ocr_v1.yaml
    └── layoutlm_resume_data.yaml
```

## Contents

### Schema Examples

- `schema/annual_report_to_markdown.yaml`: Example schema for converting Annual report to Markdown without using OCR.
- `schema/doclaynet_bench`: Example schema to convert a sample of DoclayNet [dataset](https://huggingface.co/datasets/vikp/doclaynet_bench) to Markdown
- `schema/extract_info_from_invoice.yaml`: Example schema for extracting customer data, invoice data from invoices and synthesizing new data from PDF invoices
- `schema/funsd_layoutlmv3.yaml`: Example schema to process a sample of FunSD LayoutLMv3 [dataset](https://huggingface.co/datasets/nielsr/funsd-layoutlmv3)
- `schema/generate_product_review.yaml`: Schema setup for generating and rating product reviews.
- `schema/graph_parsing.yaml`: Example schema for extracting insights from static graphs
- `schema/invoices_receipts_ocr_v1.yaml`: Example schema for processing invoices and receipts sampled from huggingface [dataset](https://huggingface.co/datasets/mychen76/invoices-and-receipts_ocr_v1).
- `schema/layoutlm_resume_data.yaml`: Example schema for parsing candidates info and experience from resumes sample from huggingface [dataset](https://huggingface.co/datasets/Kunling/layoutlm_resume_data/viewer/funsd/train?p=1).

### Exported Datasets

- `exports/doclaynet_bench/result.json`: This `jsonl` contains processed sample of [DoclayNet](https://huggingface.co/datasets/Kunling/layoutlm_resume_data/viewer/funsd/train?p=1) Benchmark dataset extracted using Cyyrus CLI.
- `exports/funsd_layoutlmv3/result.json`: This `jsonl` contains processed sample of FunSD LayoutLMv3 [dataset](https://huggingface.co/datasets/nielsr/funsd-layoutlmv3) generated using Cyyrus CLI.
- `exports/invoices_receipts_ocr_v1/result.json`: The `jsonl` contains information about the invoice items, customer information, and invoice questions and answers extracted from invoices-and-receipts [dataset](https://huggingface.co/datasets/mychen76/invoices-and-receipts_ocr_v1) using Cyyrus CLI.
- `exports/layoutlm_resume_data/result.json`: The `jsonl` contains information about the candidate's personal details, work experience, education, and skills extracted from [layoutlm_resume_dataset](https://huggingface.co/datasets/Kunling/layoutlm_resume_data/viewer/funsd/train?p=1) using Cyyrus CLI.

### Notebook

- `notebook/schema_cookbook.ipynb`: Notebook for creating and configuring schemas for Cyyrus. Or try out [![Schema Cookbook](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/18qYnYKPHiCWRqH92bzpNujJoC4dYqWS-?usp=sharing)


## Getting Started

1. Clone this repository.
2. Explore the `schema` directory for YAML configuration examples.
3. Open `schema_cookbook.ipynb` in Jupyter to interactively create and modify schemas.

For detailed documentation and usage instructions, visit our [main documentation](https://cyyrus.com).

## Contributing

Feel free to contribute your own examples by submitting a pull request!

## Support

If you have any questions or run into issues, please [open an issue](https://github.com/wizenheimer/cyyrus/issues/new/choose) on our GitHub repository.