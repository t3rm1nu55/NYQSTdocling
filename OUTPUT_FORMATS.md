# Docling Output Formats Guide

Complete guide to all output formats available in IBM Docling with examples and use cases.

## Overview

Docling supports **6 different output formats**, each optimized for different use cases:

1. **JSON** - Most comprehensive, pixel-level layout preservation
2. **HTML** - Visual rendering with styling
3. **DocTags** - Docling's native format
4. **Markdown** - Human-readable, simple formatting
5. **Plain Text** - Text extraction only
6. **Document Tokens** - Token-level data (deprecated, use DocTags)

---

## Format Comparison

### Size Comparison (2-page PDF example)

| Format | File Size | Compression | Data Richness |
|--------|-----------|-------------|---------------|
| JSON | 44 KB | None | ⭐⭐⭐⭐⭐ Complete |
| HTML | 11 KB | Medium | ⭐⭐⭐ Good |
| DocTags | 11 KB | Medium | ⭐⭐⭐⭐⭐ Complete |
| Markdown | 7.5 KB | High | ⭐⭐ Basic |
| Plain Text | 7.5 KB | High | ⭐ Minimal |
| Tokens | 11 KB | Medium | ⭐⭐⭐⭐ Rich |

### Feature Comparison

| Feature | JSON | HTML | DocTags | Markdown | Text | Tokens |
|---------|------|------|---------|----------|------|--------|
| **Pixel-level coordinates** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Page numbers** | ✅ | ⚠️ | ✅ | ❌ | ❌ | ✅ |
| **Bounding boxes** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Image metadata** | ✅ | ⚠️ | ✅ | ❌ | ❌ | ✅ |
| **Table structure** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Text formatting** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **CSS styling** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Hierarchical structure** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Element labels** | ✅ | ⚠️ | ✅ | ❌ | ❌ | ✅ |
| **Parent/child relationships** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ |
| **Character spans** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Programmatic access** | ✅✅ | ⚠️ | ✅ | ⚠️ | ✅ | ✅ |
| **Human readability** | ⚠️ | ✅✅ | ⚠️ | ✅✅ | ✅ | ❌ |

---

## 1. JSON Format - Complete Structured Data

### Description
The **most comprehensive format** that preserves **all document information** including pixel-level layout coordinates, bounding boxes, and complete metadata.

### Features
- ✅ **Pixel-level bounding boxes** for every element
- ✅ **Page coordinates** (left, top, right, bottom)
- ✅ **Element hierarchy** with parent/child relationships
- ✅ **Character spans** for text elements
- ✅ **Image metadata** (location, size, references)
- ✅ **Table data** with cell-level information
- ✅ **Programmatic access** via Python dictionaries

### Example Structure
```json
{
  "schema_name": "DoclingDocument",
  "version": "1.8.0",
  "name": "document",
  "pictures": [
    {
      "self_ref": "#/pictures/0",
      "label": "picture",
      "prov": [{
        "page_no": 1,
        "bbox": {
          "l": 110.86,    // left coordinate
          "t": 792.94,    // top coordinate
          "r": 138.02,    // right coordinate
          "b": 781.40,    // bottom coordinate
          "coord_origin": "BOTTOMLEFT"
        }
      }]
    }
  ],
  "texts": [...],
  "tables": [...],
  "body": {...}
}
```

### Use Cases
- ✅ **Layout analysis** - Precise element positioning
- ✅ **Document reconstruction** - Preserve exact layout
- ✅ **Data extraction** - Programmatic access to all elements
- ✅ **AI/ML training** - Complete document structure
- ✅ **Document comparison** - Structural diff analysis
- ✅ **Coordinate-based search** - Find elements by position

### Export Code
```python
from docling.document_converter import DocumentConverter
import json

converter = DocumentConverter()
result = converter.convert("document.pdf")

# Export to dictionary
doc_dict = result.document.export_to_dict()

# Save as JSON
with open("output.json", 'w') as f:
    json.dump(doc_dict, f, indent=2)
```

### Coordinate System
```
coord_origin: "BOTTOMLEFT"

  (0, max_y) ─────────────── (max_x, max_y)
       │                           │
       │         Page              │
       │                           │
  (0, 0) ──────────────────── (max_x, 0)
```

---

## 2. HTML Format - Visual Rendering

### Description
HTML output with **inline CSS styling** for visual rendering in web browsers.

### Features
- ✅ **Full CSS styling** for visual presentation
- ✅ **Table formatting** with borders and styling
- ✅ **Heading hierarchy** (H1-H6)
- ✅ **Figure elements** for images (placeholders)
- ✅ **Responsive design** with max-width
- ⚠️ **No pixel coordinates** in output
- ⚠️ **Images as placeholders** only

### Example Structure
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { max-width: 800px; margin: 0 auto; }
        table { border-collapse: collapse; }
        figure { text-align: center; }
    </style>
</head>
<body>
    <h1>Document Title</h1>
    <p>Document content...</p>
    <table>...</table>
    <figure>
        <figcaption>Image caption</figcaption>
    </figure>
</body>
</html>
```

### Use Cases
- ✅ **Web display** - Direct browser rendering
- ✅ **Reports** - Styled documents
- ✅ **Email** - HTML email content
- ✅ **Preview** - Quick visual check
- ✅ **Archival** - Self-contained HTML files

### Export Code
```python
html_output = result.document.export_to_html()
with open("output.html", 'w') as f:
    f.write(html_output)
```

---

## 3. DocTags Format - Native Docling Format

### Description
Docling's **native markup format** that preserves complete structure and metadata in a compact text representation.

### Features
- ✅ **Complete metadata** preservation
- ✅ **Bounding box coordinates** included
- ✅ **Element hierarchy** maintained
- ✅ **Compact representation** (~11KB vs 44KB JSON)
- ✅ **Human-readable** tags
- ✅ **Round-trip conversion** possible

### Example Structure
```
<document>
  <page number="1">
    <text label="title" bbox="[100,700,500,750]">
      Document Title
    </text>
    <picture bbox="[110,781,138,792]"/>
    <table bbox="[100,400,500,600]">
      ...
    </table>
  </page>
</document>
```

### Use Cases
- ✅ **Docling ecosystem** - Native format
- ✅ **Intermediate processing** - Pipeline workflows
- ✅ **Compact storage** - Smaller than JSON
- ✅ **Layout preservation** - With coordinates

### Export Code
```python
doctags_output = result.document.export_to_doctags()
with open("output.doctags", 'w') as f:
    f.write(doctags_output)
```

---

## 4. Markdown Format - Human-Readable

### Description
**Simplified markdown** format for human readability and easy editing.

### Features
- ✅ **Clean, readable** text
- ✅ **Heading hierarchy** (# ## ###)
- ✅ **Tables** in markdown format
- ✅ **Lists** (bullet and numbered)
- ✅ **Basic formatting** (bold, italic)
- ❌ **No coordinates** or layout info
- ❌ **No images** (placeholders only)

### Example Structure
```markdown
# Document Title

## Section Heading

This is paragraph text with **bold** and *italic* formatting.

### Subsection

- Bullet point 1
- Bullet point 2

| Column 1 | Column 2 |
|----------|----------|
| Data     | Data     |

<!-- image -->
```

### Use Cases
- ✅ **Documentation** - README files
- ✅ **Note-taking** - Simple text extraction
- ✅ **Content migration** - To markdown-based systems
- ✅ **Quick reading** - Human consumption
- ✅ **Text analysis** - NLP processing

### Export Code
```python
md_output = result.document.export_to_markdown()
with open("output.md", 'w') as f:
    f.write(md_output)
```

---

## 5. Plain Text Format - Text Only

### Description
**Pure text extraction** with no formatting or structure.

### Features
- ✅ **Text only** - No formatting
- ✅ **Lightweight** - Smallest file size
- ✅ **Simple** - Easy to process
- ❌ **No structure** - Flat text
- ❌ **No tables** - Text only
- ❌ **No metadata** - Zero context

### Example Structure
```text
Document Title
Section Heading
Subsection
This is paragraph text.
Bullet point 1
Bullet point 2
Column 1 Column 2
Data Data
```

### Use Cases
- ✅ **Text search** - Full-text indexing
- ✅ **Word count** - Simple metrics
- ✅ **Text extraction** - Raw content
- ✅ **Legacy systems** - Plain text only
- ✅ **Lightweight processing** - Minimal overhead

### Export Code
```python
text_output = result.document.export_to_text()
with open("output.txt", 'w') as f:
    f.write(text_output)
```

---

## 6. Document Tokens Format (Deprecated)

### Description
**Token-level data** format (deprecated in favor of DocTags).

### Features
- ✅ **Token-level** granularity
- ✅ **Coordinates** for tokens
- ⚠️ **Deprecated** - Use DocTags instead

### Export Code
```python
# Deprecated - use export_to_doctags() instead
tokens = result.document.export_to_document_tokens()
```

---

## Choosing the Right Format

### Decision Matrix

**Need pixel-level layout?** → Use **JSON** or **DocTags**

**Need visual rendering?** → Use **HTML**

**Need human readability?** → Use **Markdown**

**Need programmatic access?** → Use **JSON**

**Need compact size with metadata?** → Use **DocTags**

**Need text extraction only?** → Use **Plain Text**

### Recommendation by Use Case

| Use Case | Recommended Format | Alternative |
|----------|-------------------|-------------|
| Web application display | HTML | Markdown |
| Data analysis / ML | JSON | DocTags |
| Layout reconstruction | JSON | DocTags |
| Content management | Markdown | Plain Text |
| Documentation | Markdown | HTML |
| Archival with full metadata | JSON | DocTags |
| Quick preview | HTML | Markdown |
| Text search/indexing | Plain Text | Markdown |
| Coordinate-based operations | JSON | DocTags |

---

## Advanced: Accessing Layout Data

### Extract Bounding Boxes (JSON)

```python
import json

# Load JSON output
with open("document.json", 'r') as f:
    doc = json.load(f)

# Get all pictures with coordinates
for picture in doc['pictures']:
    bbox = picture['prov'][0]['bbox']
    page = picture['prov'][0]['page_no']

    print(f"Picture on page {page}:")
    print(f"  Left: {bbox['l']}")
    print(f"  Top: {bbox['t']}")
    print(f"  Right: {bbox['r']}")
    print(f"  Bottom: {bbox['b']}")
    print(f"  Width: {bbox['r'] - bbox['l']}")
    print(f"  Height: {bbox['t'] - bbox['b']}")
```

### Extract All Elements by Type

```python
# Get all tables
tables = doc.get('tables', [])

# Get all text elements
texts = doc.get('texts', [])

# Get all pictures
pictures = doc.get('pictures', [])

# Get document body structure
body = doc.get('body', {})
```

---

## Performance Comparison

### Export Time (2-page document)

| Format | Export Time | File Size | Time/KB |
|--------|-------------|-----------|---------|
| JSON | 0.05s | 44 KB | 1.1ms/KB |
| HTML | 0.03s | 11 KB | 2.7ms/KB |
| DocTags | 0.04s | 11 KB | 3.6ms/KB |
| Markdown | 0.02s | 7.5 KB | 2.7ms/KB |
| Plain Text | 0.01s | 7.5 KB | 1.3ms/KB |

**Note:** All formats export quickly. Choose based on feature needs, not performance.

---

## Summary

### Quick Reference

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")

# Export to different formats
markdown = result.document.export_to_markdown()   # Human-readable
html = result.document.export_to_html()           # Web display
doctags = result.document.export_to_doctags()     # Native format
text = result.document.export_to_text()           # Text only
data_dict = result.document.export_to_dict()      # Full data (JSON)
```

### Key Takeaways

1. **JSON format preserves EVERYTHING** - including pixel-level coordinates
2. **HTML is best for visual rendering** - styled, ready for web
3. **Markdown is most human-readable** - simple, clean text
4. **DocTags is compact with full metadata** - native Docling format
5. **Plain text is simplest** - just the text content

**For layout-aware applications, always use JSON or DocTags format!**

---

**Document Version:** 1.0
**Last Updated:** 2025-12-10
**Tested with:** Docling 2.63.0
