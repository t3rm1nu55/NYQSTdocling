# IBM Docling - Document Processing Guide for Claude

This guide explains how to use IBM Docling to process documents using both standard methods and the IBM Vision Language Model (VLM).

## Overview

IBM Docling is a powerful document processing toolkit that converts various document formats (PDF, DOCX, PPTX, XLSX, HTML, images) into structured, AI-ready formats like Markdown, HTML, and JSON. It supports advanced features like OCR, table recognition, and Vision Language Models for end-to-end document understanding.

## Installation

### Using uv (Recommended)

```bash
# Install uv if not already installed
pip install uv

# Sync dependencies from pyproject.toml
uv sync

# Or install docling directly with all features
uv add "docling[tesserocr,vlm,rapidocr]"
```

### Using pip

```bash
# Basic installation
pip install docling

# Full installation with all features
pip install "docling[tesserocr,vlm,rapidocr]"

# For macOS Apple Silicon acceleration
pip install mlx-vlm
```

## Standard Document Processing Methods

### Basic Conversion (Python API)

```python
from docling.document_converter import DocumentConverter

# Convert a document (local file or URL)
source = "path/to/document.pdf"
converter = DocumentConverter()
result = converter.convert(source)

# Export to Markdown
markdown_output = result.document.export_to_markdown()
print(markdown_output)

# Export to HTML
html_output = result.document.export_to_html()

# Export to JSON
json_output = result.document.export_to_json()
```

### Command Line Interface

```bash
# Convert PDF to Markdown
docling myfile.pdf

# Convert to multiple formats
docling myfile.pdf --to json --to md

# Convert with OCR disabled
docling myfile.pdf --to md --no-ocr

# Batch convert directory
docling ./input_dir --from pdf --to json
```

### Advanced Conversion Options

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# Configure pipeline options
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True

# Create converter with options
converter = DocumentConverter()
result = converter.convert("document.pdf")

# Access extracted components
document = result.document

# Get all tables
for table in document.tables:
    print(table.export_to_markdown())

# Get all images
for image in document.images:
    print(f"Image: {image.caption}")
```

## IBM Vision Language Model (VLM) Methods

The IBM Granite Docling VLM provides advanced end-to-end document understanding using vision-language models. This is the recommended approach for complex documents with rich layouts, tables, and mixed content.

### Using VLM via CLI

```bash
# Convert using VLM pipeline with Granite Docling model
docling --pipeline vlm --vlm-model granite_docling myfile.pdf

# Convert to HTML and Markdown with VLM
docling --to html --to md --pipeline vlm --vlm-model granite_docling myfile.pdf

# Include layout visualization
docling --to html_split_page --show-layout --pipeline vlm --vlm-model granite_docling myfile.pdf
```

### Using VLM via Python API

```python
from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.document_converter import DocumentConverter, PdfFormatOption

# Configure for VLM processing
source = "document.pdf"
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
        ),
    }
)

# Convert and export
result = converter.convert(source=source)
document = result.document
print(document.export_to_markdown())
```

### Apple Silicon Acceleration (macOS)

For M-series Mac users, use the MLX-accelerated version:

```python
from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# Configure for MLX-accelerated VLM
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_MLX,
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        ),
    }
)

result = converter.convert(source="document.pdf")
print(result.document.export_to_markdown())
```

### GPU Acceleration (CUDA)

For NVIDIA GPU acceleration:

```bash
# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

```python
from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# VLM will automatically use GPU if available
pipeline_options = VlmPipelineOptions()

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        ),
    }
)

result = converter.convert(source="document.pdf")
```

## OCR Engine Options

Docling supports multiple OCR engines:

### Tesseract OCR
```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options = TesseractOcrOptions()
```

### RapidOCR (ONNX-based)
```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options = RapidOcrOptions()
```

### EasyOCR
```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options = EasyOcrOptions()
```

## Supported Formats

### Input Formats
- **Documents**: PDF, DOCX, PPTX, XLSX
- **Web**: HTML
- **Images**: PNG, JPG, JPEG, TIFF, BMP
- **Audio**: WAV, MP3, VTT (with ASR support)

### Output Formats
- **Markdown**: Preserves structure, tables, and formatting
- **HTML**: Full HTML with styling
- **JSON**: Structured data representation
- **DocTags**: Docling's native markup format

## Best Practices

### When to Use Standard Pipeline
- Simple text-heavy documents
- Documents with clear layouts
- When speed is more important than accuracy
- Processing many documents in batch

### When to Use VLM Pipeline
- Complex documents with mixed content
- Documents with dense tables and figures
- Scanned documents or images
- When accuracy is critical
- Documents in multiple languages

### Performance Tips
1. Use `--no-ocr` flag when documents are text-based PDFs
2. Batch process multiple files in a single directory
3. Use GPU acceleration for VLM processing when available
4. For production, consider using the Docker image with all dependencies

## Example Workflow

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.document_converter import PdfFormatOption
import os

def process_documents(input_dir: str, output_dir: str, use_vlm: bool = False):
    """Process all documents in a directory."""
    
    # Configure converter
    if use_vlm:
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                ),
            }
        )
    else:
        converter = DocumentConverter()
    
    # Process each file
    for filename in os.listdir(input_dir):
        if filename.endswith(('.pdf', '.docx', '.pptx')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{filename}.md")
            
            # Convert
            result = converter.convert(input_path)
            
            # Save as Markdown
            with open(output_path, 'w') as f:
                f.write(result.document.export_to_markdown())
            
            print(f"Processed: {filename}")

# Usage
process_documents("./documents", "./output", use_vlm=True)
```

## Troubleshooting

### Common Issues

1. **OCR not working**: Ensure Tesseract is installed on your system
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # macOS
   brew install tesseract
   ```

2. **VLM model download fails**: Check your internet connection and disk space

3. **Out of memory with VLM**: Reduce batch size or use CPU instead of GPU

4. **Slow processing**: Consider using the standard pipeline for simpler documents

## References

- [Docling Documentation](https://docling-project.github.io/docling/)
- [Docling GitHub Repository](https://github.com/docling-project/docling)
- [IBM Granite Docling Model](https://www.ibm.com/granite/docs/models/docling)
- [Hugging Face Model Card](https://huggingface.co/ibm-granite/granite-docling-258M)
