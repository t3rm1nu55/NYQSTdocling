# NYQSTdocling

IBM Docling document processing setup with Vision Language Model (VLM) support.

## Overview

This repository provides a ready-to-use setup for IBM Docling, a powerful document processing toolkit that converts various document formats into structured, AI-ready outputs. It includes support for both standard processing methods and the IBM Granite Vision Language Model for advanced document understanding.

## Features

- **Multi-format Support**: Process PDF, DOCX, PPTX, XLSX, HTML, and images
- **Multiple OCR Engines**: Tesseract, RapidOCR, EasyOCR
- **Vision Language Model**: IBM Granite Docling for end-to-end document understanding
- **Flexible Output**: Export to Markdown, HTML, JSON
- **uv Package Management**: Fast, modern Python dependency management

## Quick Start

### Prerequisites

- Python 3.9 - 3.12
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd NYQSTdocling

# Install dependencies with uv
uv sync
```

### Basic Usage

```python
from docling.document_converter import DocumentConverter

# Convert a document
converter = DocumentConverter()
result = converter.convert("document.pdf")

# Export to Markdown
print(result.document.export_to_markdown())
```

### Using IBM Vision Model

```bash
docling --pipeline vlm --vlm-model granite_docling document.pdf
```

## Documentation

See [claude.md](claude.md) for comprehensive usage documentation including:
- Standard document processing methods
- IBM Vision Language Model usage
- OCR engine configuration
- Performance optimization tips

## Dependencies

Core dependencies managed via `pyproject.toml`:
- `docling[tesserocr,vlm,rapidocr]` - Core document processing
- `torch`, `torchvision`, `transformers` - VLM support
- `easyocr` - Additional OCR engine
- `pillow`, `pypdf` - Document utilities

## License

This project uses IBM Docling which is licensed under Apache 2.0.