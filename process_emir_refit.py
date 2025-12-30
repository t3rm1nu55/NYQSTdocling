#!/usr/bin/env python3
"""
Process ESMA EMIR REFIT Guidelines with Docling using specific high-quality settings.
"""

import logging
import time
import json
import requests
import pandas as pd
import argparse
import sys
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
PDF_URL = "https://www.esma.europa.eu/sites/default/files/2023-10/ESMA74-362-2281_Guidelines_EMIR_REFIT.pdf"
OUTPUT_DIR = Path("output/emir_refit")
PDF_FILENAME = "ESMA_Guidelines_EMIR_REFIT.pdf"

def setup_pipeline_options():
    """
    Configure PdfPipelineOptions with:
    - Quality best (implied by enabling enrichments and OCR)
    - OCR: on
    - VLM: on (via picture description)
    - Equations: off
    - Code: on
    - ASR: off (irrelevant for PDF)
    - Image capture: on
    - Image scaling: 2x
    - Table analysis: full (including cell analysis)
    - Content tagging: on (via picture classification/description)
    """
    pipeline_options = PdfPipelineOptions()

    # OCR on
    pipeline_options.do_ocr = True
    # pipeline_options.ocr_options = TesseractOcrOptions() # Default is usually fine

    # Table analysis full
    pipeline_options.do_table_structure = True
    # Note: cell analysis is part of table structure in docling

    # Equations off
    pipeline_options.do_formula_enrichment = False

    # Code on
    pipeline_options.do_code_enrichment = True

    # Image capture on & Scaling 2x
    pipeline_options.generate_page_images = True
    pipeline_options.images_scale = 2.0

    # Content tagging / VLM on if possible
    # We enable picture classification and description which uses VLM models
    pipeline_options.do_picture_classification = True
    pipeline_options.do_picture_description = True

    return pipeline_options

def download_pdf(url: str, output_path: Path):
    """Downloads the PDF if it doesn't exist."""
    if output_path.exists():
        logging.info(f"PDF already exists at {output_path}")
        return

    logging.info(f"Downloading PDF from {url}...")
    try:
        response = requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info(f"Downloaded PDF to {output_path}")
    except Exception as e:
        logging.error(f"Failed to download PDF: {e}")
        raise

def save_outputs(result, output_base_name: str, step_name: str):
    """Saves the result to JSON and Parquet."""
    output_dir = OUTPUT_DIR / step_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = output_dir / f"{output_base_name}.json"
    with open(json_path, 'w') as f:
        json.dump(result.document.export_to_dict(), f, indent=2)
    logging.info(f"Saved JSON to {json_path}")

    # Save Markdown for quick inspection
    md_path = output_dir / f"{output_base_name}.md"
    with open(md_path, 'w') as f:
        f.write(result.document.export_to_markdown())
    logging.info(f"Saved Markdown to {md_path}")

    # Save Parquet
    text_items = []
    for item in result.document.texts:
        text_items.append({
            "type": "text",
            "text": item.text,
            "label": item.label,
            "page_no": item.prov[0].page_no if item.prov else None
        })

    table_items = []
    for i, table in enumerate(result.document.tables):
        table_items.append({
            "type": "table",
            "text": table.export_to_markdown(),
            "label": "table",
            "page_no": table.prov[0].page_no if table.prov else None,
            "table_index": i
        })

    df = pd.DataFrame(text_items + table_items)
    parquet_path = output_dir / f"{output_base_name}.parquet"
    df.to_parquet(parquet_path)
    logging.info(f"Saved Parquet to {parquet_path}")

def get_total_pages(pdf_path: Path) -> int:
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(pdf_path)
    return len(pdf)

def run_step(step: str, converter: DocumentConverter, pdf_path: Path):
    if step == "test":
        logging.info("Starting Test Run (First 3 pages)...")
        start_time = time.time()
        result = converter.convert(pdf_path, page_range=(1, 3))
        elapsed = time.time() - start_time
        logging.info(f"Test Run completed in {elapsed:.2f}s")
        save_outputs(result, "emir_refit_test_3pages", "01_test_run")

    elif step == "quarter":
        total_pages = get_total_pages(pdf_path)
        quarter_pages = max(1, total_pages // 4)
        logging.info(f"Starting 1/4 Run ({quarter_pages} pages)...")
        start_time = time.time()
        result = converter.convert(pdf_path, page_range=(1, quarter_pages))
        elapsed = time.time() - start_time
        logging.info(f"1/4 Run completed in {elapsed:.2f}s")
        save_outputs(result, f"emir_refit_quarter_{quarter_pages}pages", "02_quarter_run")

    elif step == "full":
        logging.info("Starting Full Run (All pages)...")
        start_time = time.time()
        result = converter.convert(pdf_path)
        elapsed = time.time() - start_time
        logging.info(f"Full Run completed in {elapsed:.2f}s")
        save_outputs(result, "emir_refit_full", "03_full_run")

def main():
    parser = argparse.ArgumentParser(description="Process ESMA EMIR REFIT Guidelines")
    parser.add_argument("--step", choices=["test", "quarter", "full", "all"], default="all", help="Which step to run")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUTPUT_DIR / PDF_FILENAME

    # 1. Download
    download_pdf(PDF_URL, pdf_path)

    # 2. Configure Converter
    pipeline_opts = setup_pipeline_options()
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)
        }
    )

    # 3. Run Steps
    if args.step == "all":
        run_step("test", converter, pdf_path)
        run_step("quarter", converter, pdf_path)
        run_step("full", converter, pdf_path)
    else:
        run_step(args.step, converter, pdf_path)

if __name__ == "__main__":
    main()
