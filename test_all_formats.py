#!/usr/bin/env python3
"""
Test all docling export formats to show differences in output quality.
"""

import json
from pathlib import Path
from docling.document_converter import DocumentConverter

def test_all_export_formats(pdf_path: Path):
    """Export document in all available formats."""

    print(f"Processing: {pdf_path.name}")
    print("="*80)

    # Convert document
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    doc = result.document

    output_dir = Path("output/all_formats")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = pdf_path.stem

    # 1. Markdown
    print("\n1. Exporting to Markdown...")
    md_output = doc.export_to_markdown()
    md_file = output_dir / f"{base_name}.md"
    md_file.write_text(md_output)
    print(f"   ✓ Saved: {md_file} ({len(md_output)/1024:.2f} KB)")

    # 2. HTML
    print("\n2. Exporting to HTML...")
    html_output = doc.export_to_html()
    html_file = output_dir / f"{base_name}.html"
    html_file.write_text(html_output)
    print(f"   ✓ Saved: {html_file} ({len(html_output)/1024:.2f} KB)")

    # 3. DocTags (Docling's native format)
    print("\n3. Exporting to DocTags...")
    doctags_output = doc.export_to_doctags()
    doctags_file = output_dir / f"{base_name}.doctags"
    doctags_file.write_text(doctags_output)
    print(f"   ✓ Saved: {doctags_file} ({len(doctags_output)/1024:.2f} KB)")

    # 4. Plain Text
    print("\n4. Exporting to Plain Text...")
    text_output = doc.export_to_text()
    text_file = output_dir / f"{base_name}.txt"
    text_file.write_text(text_output)
    print(f"   ✓ Saved: {text_file} ({len(text_output)/1024:.2f} KB)")

    # 5. Dictionary/JSON
    print("\n5. Exporting to JSON (dict)...")
    dict_output = doc.export_to_dict()
    json_file = output_dir / f"{base_name}.json"
    with open(json_file, 'w') as f:
        json.dump(dict_output, f, indent=2)
    print(f"   ✓ Saved: {json_file} ({json_file.stat().st_size/1024:.2f} KB)")

    # 6. Document Tokens
    print("\n6. Exporting to Document Tokens...")
    tokens = doc.export_to_document_tokens()
    tokens_file = output_dir / f"{base_name}_tokens.json"
    with open(tokens_file, 'w') as f:
        json.dump(tokens, f, indent=2)
    print(f"   ✓ Saved: {tokens_file} ({tokens_file.stat().st_size/1024:.2f} KB)")

    print("\n" + "="*80)
    print("✅ All formats exported!")
    print("="*80)

    # Show format comparison
    print("\n📊 Format Comparison:")
    print(f"{'Format':<20} {'Size (KB)':<15} {'Features'}")
    print("-"*80)
    print(f"{'Markdown':<20} {len(md_output)/1024:<15.2f} Structure, tables, basic formatting")
    print(f"{'HTML':<20} {len(html_output)/1024:<15.2f} Full styling, layout, visual elements")
    print(f"{'DocTags':<20} {len(doctags_output)/1024:<15.2f} Native format, all metadata")
    print(f"{'Plain Text':<20} {len(text_output)/1024:<15.2f} Text only, no formatting")
    print(f"{'JSON':<20} {json_file.stat().st_size/1024:<15.2f} Structured data, programmatic access")
    print(f"{'Tokens':<20} {tokens_file.stat().st_size/1024:<15.2f} Token-level data")

    # Check for images and pictures in document
    print("\n📸 Document Analysis:")
    print(f"   Pages: {len(doc.pages) if hasattr(doc, 'pages') else 'N/A'}")
    print(f"   Tables: {len(doc.tables) if hasattr(doc, 'tables') else 'N/A'}")
    print(f"   Pictures: {len(doc.pictures) if hasattr(doc, 'pictures') else 'N/A'}")

    # Show JSON structure preview
    print("\n📋 JSON Structure Keys:")
    if isinstance(dict_output, dict):
        for key in list(dict_output.keys())[:10]:
            print(f"   - {key}")

    return output_dir

if __name__ == "__main__":
    # Test with the 2-page test PDF
    test_pdf = Path("output/test_2page.pdf")

    if test_pdf.exists():
        output_dir = test_all_export_formats(test_pdf)
        print(f"\n📁 All outputs saved to: {output_dir.absolute()}")
    else:
        print(f"Error: Test PDF not found: {test_pdf}")
