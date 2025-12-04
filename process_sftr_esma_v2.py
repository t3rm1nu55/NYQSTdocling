#!/usr/bin/env python3
"""
Process SFTR EUR-LEX and ESMA documents with Docling using different processing modes.
Measures performance and saves results to output folder.
Uses requests library for downloading.
"""

import asyncio
import time
import platform
import psutil
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.pipeline.vlm_pipeline import VlmPipeline


# Document URLs to process
DOCUMENT_URLS = {
    "SFTR_Regulation_PDF": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32015R2365",
    "SFTR_Delegated_Reg": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32019R0356",
    # Add fallback/alternative URLs if primary ones fail
}


def get_system_specs() -> Dict:
    """Collect system specifications."""
    import torch

    specs = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(logical=False),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "cuda_available": torch.cuda.is_available(),
    }

    if specs["cuda_available"]:
        specs["cuda_device_count"] = torch.cuda.device_count()
        specs["cuda_device_name"] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None
        specs["cuda_version"] = torch.version.cuda

    return specs


def download_file(url: str, output_path: Path, timeout: int = 300) -> bool:
    """Download file using requests."""
    try:
        print(f"  Downloading: {url}")
        response = requests.get(url, timeout=timeout, stream=True,
                              headers={'User-Agent': 'Mozilla/5.0'})

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"    ✓ Saved to {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")
            return True
        else:
            print(f"    ✗ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False


def download_all_documents(output_dir: Path) -> Dict[str, Path]:
    """Download all documents."""
    downloads_dir = output_dir / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files = {}

    for name, url in DOCUMENT_URLS.items():
        file_path = downloads_dir / f"{name}.pdf"
        if download_file(url, file_path):
            downloaded_files[name] = file_path

    return downloaded_files


def process_document_quick(file_path: Path) -> Tuple[str, float, Dict]:
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

    stats = {
        "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
        "tables": len(result.document.tables) if hasattr(result.document, 'tables') else 0,
    }

    return output, elapsed, stats


def process_document_slow(file_path: Path) -> Tuple[str, float, Dict]:
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

    stats = {
        "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
        "tables": len(result.document.tables) if hasattr(result.document, 'tables') else 0,
    }

    return output, elapsed, stats


def process_document_accurate(file_path: Path) -> Tuple[str, float, Dict]:
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

    stats = {
        "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
        "tables": len(result.document.tables) if hasattr(result.document, 'tables') else 0,
    }

    return output, elapsed, stats


def process_document_vlm(file_path: Path) -> Tuple[str, float, Dict]:
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

    stats = {
        "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
        "tables": len(result.document.tables) if hasattr(result.document, 'tables') else 0,
    }

    return output, elapsed, stats


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

    print(f"\n📄 Processing: {doc_name} ({results['file_size_mb']} MB)")

    for mode in processing_modes:
        if mode not in processors:
            continue

        print(f"  ⚙️  {mode.upper()} mode...", end=" ", flush=True)

        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            output, elapsed, stats = await loop.run_in_executor(
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
                "stats": stats,
            }

            print(f"✓ {elapsed:.2f}s (Pages: {stats.get('pages', 0)}, Tables: {stats.get('tables', 0)})")

        except Exception as e:
            results["modes"][mode] = {
                "status": "failed",
                "error": str(e),
            }
            print(f"✗ {e}")

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
    print(f"   CUDA Available: {system_specs['cuda_available']}")
    if system_specs['cuda_available']:
        print(f"   GPU: {system_specs.get('cuda_device_name', 'Unknown')}")
    print()

    # Download documents
    print("📥 Downloading documents...")
    downloaded_files = download_all_documents(output_dir)
    print(f"\n   ✓ Downloaded {len(downloaded_files)} file(s)")
    print()

    if not downloaded_files:
        print("❌ No files downloaded. Exiting.")
        return

    # Processing modes to use
    processing_modes = ["quick", "slow", "accurate", "vlm"]

    # Process all documents
    print("=" * 80)
    print("🔄 PROCESSING DOCUMENTS")
    print(f"   Modes: {', '.join(m.upper() for m in processing_modes)}")
    print("=" * 80)

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

    print(f"💾 Summary saved to: {summary_file}")
    print()

    # Print timing table
    print("⏱️  Processing Times (seconds):")
    print()
    print(f"{'Document':<35} {'Quick':<12} {'Slow':<12} {'Accurate':<12} {'VLM':<12}")
    print("-" * 83)

    for result in all_results:
        doc_name = result['document'][:33]
        quick = result['modes'].get('quick', {}).get('time_seconds', '-')
        slow = result['modes'].get('slow', {}).get('time_seconds', '-')
        accurate = result['modes'].get('accurate', {}).get('time_seconds', '-')
        vlm = result['modes'].get('vlm', {}).get('time_seconds', '-')

        print(f"{doc_name:<35} {str(quick):<12} {str(slow):<12} {str(accurate):<12} {str(vlm):<12}")

    print()
    print("=" * 80)
    print("✅ Processing complete!")
    print(f"   📁 Results saved to: {output_dir.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
