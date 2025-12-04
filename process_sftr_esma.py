#!/usr/bin/env python3
"""
Process SFTR EUR-LEX and ESMA documents with Docling using different processing modes.
Measures performance and saves results to output folder.
"""

import asyncio
import time
import platform
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import aiohttp
import tempfile

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.pipeline.vlm_pipeline import VlmPipeline


# Document URLs to process
SFTR_EURLEX_URLS = {
    "SFTR_PDF": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32015R2365",
    "SFTR_HTML": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32015R2365",
    "SFTR_XML": "https://eur-lex.europa.eu/legal-content/EN/TXT/XML/?uri=CELEX:32015R2365",
}

ESMA_GUIDANCE_URLS = {
    "ESMA_SFTR_Guidelines": "https://www.esma.europa.eu/sites/default/files/library/esma70-151-1218_sftr_guidelines_on_reporting.pdf",
    "ESMA_SFTR_QA": "https://www.esma.europa.eu/sites/default/files/library/esma70-1861941480-56_qa_on_sftr_implementation.pdf",
}


def get_system_specs() -> Dict:
    """Collect system specifications."""
    return {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(logical=False),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
    }


async def download_file(session: aiohttp.ClientSession, url: str, output_path: Path) -> bool:
    """Download file asynchronously."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response:
            if response.status == 200:
                content = await response.read()
                output_path.write_bytes(content)
                return True
            else:
                print(f"Failed to download {url}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


async def download_all_documents(output_dir: Path) -> Dict[str, Path]:
    """Download all documents asynchronously."""
    downloads_dir = output_dir / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files = {}

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Download SFTR EUR-LEX files
        for name, url in SFTR_EURLEX_URLS.items():
            ext = name.split('_')[-1].lower()
            file_path = downloads_dir / f"{name}.{ext}"
            tasks.append((name, download_file(session, url, file_path), file_path))

        # Download ESMA files
        for name, url in ESMA_GUIDANCE_URLS.items():
            file_path = downloads_dir / f"{name}.pdf"
            tasks.append((name, download_file(session, url, file_path), file_path))

        # Wait for all downloads
        for name, task, file_path in tasks:
            if await task:
                downloaded_files[name] = file_path
                print(f"✓ Downloaded: {name}")
            else:
                print(f"✗ Failed: {name}")

    return downloaded_files


def process_document_quick(file_path: Path) -> Tuple[str, float]:
    """Process document in quick mode (no OCR)."""
    start_time = time.time()

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(str(file_path))
    output = result.document.export_to_markdown()

    elapsed = time.time() - start_time
    return output, elapsed


def process_document_slow(file_path: Path) -> Tuple[str, float]:
    """Process document in slow mode (with OCR and full table structure)."""
    start_time = time.time()

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.ocr_options = TesseractOcrOptions()

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(str(file_path))
    output = result.document.export_to_markdown()

    elapsed = time.time() - start_time
    return output, elapsed


def process_document_accurate(file_path: Path) -> Tuple[str, float]:
    """Process document in most accurate mode (all features enabled)."""
    start_time = time.time()

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.ocr_options = TesseractOcrOptions()

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(str(file_path))
    output = result.document.export_to_markdown()

    elapsed = time.time() - start_time
    return output, elapsed


def process_document_vlm(file_path: Path) -> Tuple[str, float]:
    """Process document using IBM Granite Docling VLM."""
    start_time = time.time()

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )

    result = converter.convert(str(file_path))
    output = result.document.export_to_markdown()

    elapsed = time.time() - start_time
    return output, elapsed


async def process_document_async(
    file_path: Path,
    doc_name: str,
    output_dir: Path,
    processing_modes: List[str]
) -> Dict:
    """Process a document with all modes asynchronously."""
    results = {
        "document": doc_name,
        "file_path": str(file_path),
        "file_size_mb": round(file_path.stat().st_size / (1024**2), 2),
        "modes": {}
    }

    processors = {
        "quick": process_document_quick,
        "slow": process_document_slow,
        "accurate": process_document_accurate,
        "vlm": process_document_vlm,
    }

    for mode in processing_modes:
        if mode not in processors:
            continue

        print(f"  Processing {doc_name} with {mode} mode...")

        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            output, elapsed = await loop.run_in_executor(
                None, processors[mode], file_path
            )

            # Save output
            mode_dir = output_dir / mode
            mode_dir.mkdir(parents=True, exist_ok=True)
            output_file = mode_dir / f"{doc_name}.md"
            output_file.write_text(output)

            results["modes"][mode] = {
                "status": "success",
                "time_seconds": round(elapsed, 2),
                "output_file": str(output_file),
                "output_size_kb": round(len(output) / 1024, 2),
            }

            print(f"    ✓ {mode}: {elapsed:.2f}s")

        except Exception as e:
            results["modes"][mode] = {
                "status": "failed",
                "error": str(e),
            }
            print(f"    ✗ {mode}: {e}")

    return results


async def main():
    """Main processing function."""
    print("=" * 80)
    print("SFTR EUR-LEX and ESMA Document Processing with Docling")
    print("=" * 80)
    print()

    # Setup output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Collect system specs
    print("📊 Collecting system specifications...")
    system_specs = get_system_specs()
    print(f"   Platform: {system_specs['platform']}")
    print(f"   CPUs: {system_specs['cpu_count']} physical, {system_specs['cpu_count_logical']} logical")
    print(f"   Memory: {system_specs['total_memory_gb']} GB total, {system_specs['available_memory_gb']} GB available")
    print()

    # Download documents
    print("📥 Downloading documents...")
    downloaded_files = await download_all_documents(output_dir)
    print(f"   Downloaded {len(downloaded_files)} files")
    print()

    # Processing modes to use
    processing_modes = ["quick", "slow", "accurate", "vlm"]

    # Process all documents
    print("🔄 Processing documents with multiple modes...")
    print(f"   Modes: {', '.join(processing_modes)}")
    print()

    all_results = []

    # Process documents concurrently
    tasks = []
    for doc_name, file_path in downloaded_files.items():
        # Only process PDF files with docling
        if file_path.suffix.lower() == '.pdf':
            tasks.append(process_document_async(file_path, doc_name, output_dir, processing_modes))

    all_results = await asyncio.gather(*tasks)

    # Generate summary report
    print()
    print("=" * 80)
    print("📈 RESULTS SUMMARY")
    print("=" * 80)
    print()

    summary = {
        "system_specs": system_specs,
        "processing_date": datetime.now().isoformat(),
        "total_documents": len(all_results),
        "documents": all_results,
    }

    # Save summary to JSON
    summary_file = output_dir / "processing_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Summary saved to: {summary_file}")
    print()

    # Print timing table
    print("⏱️  Processing Times (seconds):")
    print()
    print(f"{'Document':<30} {'Quick':<10} {'Slow':<10} {'Accurate':<10} {'VLM':<10}")
    print("-" * 70)

    for result in all_results:
        doc_name = result['document'][:28]
        quick = result['modes'].get('quick', {}).get('time_seconds', '-')
        slow = result['modes'].get('slow', {}).get('time_seconds', '-')
        accurate = result['modes'].get('accurate', {}).get('time_seconds', '-')
        vlm = result['modes'].get('vlm', {}).get('time_seconds', '-')

        print(f"{doc_name:<30} {str(quick):<10} {str(slow):<10} {str(accurate):<10} {str(vlm):<10}")

    print()
    print("=" * 80)
    print("✅ Processing complete!")
    print(f"   Results saved to: {output_dir.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
