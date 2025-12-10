#!/usr/bin/env python3
"""
Test VLM mode with a small document by extracting first 2 pages.
"""

import time
from pathlib import Path
from pypdf import PdfReader, PdfWriter

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.vlm_pipeline import VlmPipeline

def create_small_test_pdf(input_pdf: Path, output_pdf: Path, num_pages: int = 2):
    """Extract first N pages to create a small test PDF."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Add first N pages
    for i in range(min(num_pages, len(reader.pages))):
        writer.add_page(reader.pages[i])

    # Write to output
    with open(output_pdf, 'wb') as f:
        writer.write(f)

    print(f"Created test PDF with {min(num_pages, len(reader.pages))} pages")
    return output_pdf

def test_vlm_mode(pdf_path: Path):
    """Test VLM mode on a small PDF."""
    print(f"\n{'='*80}")
    print("Testing IBM Granite Docling VLM Mode")
    print(f"{'='*80}\n")

    print(f"📄 Processing: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.2f} KB")

    # Initialize VLM pipeline
    print("\n⚙️  Initializing VLM pipeline with IBM Granite model...")
    start_time = time.time()

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )

    init_time = time.time() - start_time
    print(f"   ✓ Pipeline initialized in {init_time:.2f}s")

    # Process document
    print("\n🔄 Processing document with VLM...")
    process_start = time.time()

    result = converter.convert(str(pdf_path))
    output = result.document.export_to_markdown()

    process_time = time.time() - process_start
    total_time = time.time() - start_time

    # Save output
    output_path = Path("output") / "vlm_test" / f"{pdf_path.stem}_vlm.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output)

    # Print results
    print(f"\n{'='*80}")
    print("✅ VLM Processing Complete!")
    print(f"{'='*80}")
    print(f"\n⏱️  Performance:")
    print(f"   Pipeline initialization: {init_time:.2f}s")
    print(f"   Document processing: {process_time:.2f}s")
    print(f"   Total time: {total_time:.2f}s")
    print(f"\n📊 Output:")
    print(f"   Size: {len(output) / 1024:.2f} KB")
    print(f"   Saved to: {output_path}")

    # Show first few lines
    print(f"\n📝 Output Preview (first 500 chars):")
    print("-" * 80)
    print(output[:500])
    print("..." if len(output) > 500 else "")
    print("-" * 80)

if __name__ == "__main__":
    # Create small test PDF from SFTR Delegated Regulation (smaller, 21 pages)
    source_pdf = Path("output/downloads/SFTR_Delegated_Reg.pdf")
    test_pdf = Path("output/test_2page.pdf")

    if source_pdf.exists():
        print("Creating small 2-page test PDF...")
        create_small_test_pdf(source_pdf, test_pdf, num_pages=2)

        print("\n" + "="*80)
        print("Testing VLM Mode on Small Document")
        print("="*80)

        test_vlm_mode(test_pdf)
    else:
        print(f"Error: Source PDF not found: {source_pdf}")
