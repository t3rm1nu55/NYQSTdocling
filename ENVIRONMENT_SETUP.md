# Environment Setup Guide

Complete documentation for setting up the SFTR/ESMA document processing environment with IBM Docling.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Python Environment Setup](#python-environment-setup)
3. [Dependencies Installation](#dependencies-installation)
4. [Tesseract OCR Configuration](#tesseract-ocr-configuration)
5. [GPU Configuration (Optional)](#gpu-configuration-optional)
6. [Project Structure](#project-structure)
7. [Running the Processing](#running-the-processing)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS:** Linux, macOS, or Windows
- **Python:** 3.9 - 3.12
- **RAM:** 8 GB minimum, 16 GB recommended
- **Storage:** 10 GB free space (for dependencies and models)
- **CPU:** Multi-core processor recommended

### Recommended for Optimal Performance
- **RAM:** 16 GB or more
- **GPU:** NVIDIA GPU with CUDA support (for VLM mode)
- **CPU:** 8+ cores for parallel processing
- **Storage:** SSD with 20+ GB free space

### Environment Specifications (This Setup)
```
Platform: Linux 4.4.0 x86_64
CPU: 16 physical cores, 16 logical cores
Memory: 13 GB total
CUDA: Not available (CPU-only processing)
Python: 3.11.14
```

---

## Python Environment Setup

### 1. Install uv Package Manager

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that replaces pip.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd NYQSTdocling
```

### 3. Create Virtual Environment

```bash
# uv automatically creates and manages the virtual environment
# when you run sync
uv sync
```

This creates a `.venv` directory with all dependencies installed.

---

## Dependencies Installation

### Core Dependencies

The project uses `pyproject.toml` for dependency management:

```toml
[project]
dependencies = [
    # Core docling with all features
    "docling[tesserocr,vlm,rapidocr]",

    # Additional OCR engines
    "easyocr",

    # Vision Language Model support
    "torch",
    "torchvision",
    "transformers",

    # Document processing utilities
    "pillow",
    "pypdf",

    # Data handling
    "pandas",
    "numpy",

    # API and web utilities
    "requests",
    "httpx",
    "aiohttp",

    # System utilities
    "psutil",

    # Output formatting
    "markdown",
    "beautifulsoup4",
    "lxml",
]
```

### Installation Command

```bash
# Sync all dependencies from pyproject.toml
uv sync

# This installs 313 packages including:
# - docling 2.63.0
# - torch 2.9.0
# - transformers 4.57.3
# - And many more...
```

### Installation Time

- **First time:** 4-5 minutes (downloading ~5 GB of packages)
- **Subsequent syncs:** < 30 seconds (cached)

### Key Packages Installed

| Package | Version | Purpose |
|---------|---------|---------|
| docling | 2.63.0 | Core document processing |
| torch | 2.9.0 | Deep learning framework |
| transformers | 4.57.3 | HuggingFace models |
| tesserocr | 2.9.1 | Python wrapper for Tesseract |
| easyocr | 1.7.2 | Alternative OCR engine |
| rapidocr | 3.4.2 | ONNX-based OCR |
| vllm | 0.11.2 | Vision Language Model support |
| aiohttp | 3.13.2 | Async HTTP requests |
| psutil | 7.1.3 | System monitoring |

---

## Tesseract OCR Configuration

### 1. Install Tesseract (Linux/Ubuntu)

```bash
# Update package list
sudo apt-get update

# Install Tesseract and English language data
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Verify installation
tesseract --version
```

**Output:**
```
tesseract 5.3.4
```

### 2. Configure TESSDATA_PREFIX

Tesseract requires the `TESSDATA_PREFIX` environment variable to locate language data files.

```bash
# Find tessdata location
find /usr -name "tessdata" -type d

# Typical location: /usr/share/tesseract-ocr/5/tessdata

# Set environment variable (add to ~/.bashrc or ~/.zshrc for persistence)
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Verify language data is present
ls -lh $TESSDATA_PREFIX/eng.traineddata
```

### 3. Install Additional Languages (Optional)

```bash
# Install other languages as needed
sudo apt-get install -y tesseract-ocr-fra  # French
sudo apt-get install -y tesseract-ocr-deu  # German
sudo apt-get install -y tesseract-ocr-spa  # Spanish
```

### macOS Installation

```bash
# Using Homebrew
brew install tesseract

# Language data is typically in:
# /usr/local/share/tessdata (Intel)
# /opt/homebrew/share/tessdata (Apple Silicon)

export TESSDATA_PREFIX=/usr/local/share/tessdata
```

---

## GPU Configuration (Optional)

### Check GPU Availability

```bash
# Check if NVIDIA GPU is available
nvidia-smi

# Check CUDA in PyTorch
.venv/bin/python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### Install CUDA Support (if GPU available)

If you have an NVIDIA GPU but CUDA is not available:

```bash
# Install PyTorch with CUDA support
# Replace cu118 with your CUDA version (11.8, 12.1, etc.)
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Apple Silicon (M1/M2/M3) Acceleration

For Apple Silicon Macs, install MLX for hardware acceleration:

```bash
uv add mlx-vlm
```

Then use the MLX-accelerated VLM pipeline in your code.

---

## Project Structure

```
NYQSTdocling/
├── .venv/                          # Virtual environment (created by uv)
├── .gitignore                      # Git ignore rules
├── pyproject.toml                  # Project dependencies
├── uv.lock                         # Locked dependency versions
├── README.md                       # Project overview
├── claude.md                       # Docling usage guide
├── ENVIRONMENT_SETUP.md            # This file
│
├── nyqstdocling/                   # Python package
│   └── __init__.py
│
├── process_sftr_esma.py           # Initial processing script
├── process_sftr_esma_v2.py        # Main processing script
├── run_all_modes.sh               # Shell script to run all modes
│
└── output/                        # Processing outputs
    ├── downloads/                 # Downloaded PDFs
    │   ├── SFTR_Regulation_PDF.pdf
    │   └── SFTR_Delegated_Reg.pdf
    ├── quick/                     # Quick mode outputs
    │   ├── SFTR_Regulation_PDF.md
    │   └── SFTR_Delegated_Reg.md
    ├── slow/                      # SLOW mode outputs (with OCR)
    │   └── SFTR_Regulation_PDF.md
    ├── accurate/                  # ACCURATE mode outputs
    └── vlm/                       # VLM mode outputs
```

---

## Running the Processing

### Method 1: Using the Shell Script (Recommended)

```bash
# Make script executable
chmod +x run_all_modes.sh

# Run all processing modes
./run_all_modes.sh
```

This script:
- Sets `TESSDATA_PREFIX` for OCR
- Cleans previous outputs
- Runs all 4 processing modes
- Logs output to `processing_full_run.log`

### Method 2: Direct Python Execution

```bash
# Set Tesseract path
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Run processing script
.venv/bin/python process_sftr_esma_v2.py
```

### Method 3: Running Individual Modes

Modify `process_sftr_esma_v2.py` to run specific modes:

```python
# In main() function, change:
processing_modes = ["quick"]  # Only run quick mode

# Or:
processing_modes = ["quick", "slow"]  # Run quick and slow only
```

---

## Processing Modes Explained

### QUICK Mode
- **Purpose:** Fast text extraction from text-based PDFs
- **OCR:** Disabled
- **Speed:** ~2-3 minutes per 20-30 page document
- **Use Case:** Clean, text-based regulatory documents
- **Resource Usage:** Low (2-4 GB RAM, 40-60% CPU)

### SLOW Mode
- **Purpose:** OCR-enhanced extraction
- **OCR:** Enabled with Tesseract
- **Speed:** ~1-2 minutes per document (if already text-based)
- **Use Case:** Scanned documents or mixed content
- **Resource Usage:** Medium (4-6 GB RAM, 60-80% CPU)

### ACCURATE Mode
- **Purpose:** Maximum accuracy with all features
- **OCR:** Enabled with advanced options
- **Speed:** ~1-2 minutes per document
- **Use Case:** Critical documents requiring highest accuracy
- **Resource Usage:** Medium-High (4-8 GB RAM, 60-80% CPU)

### VLM Mode (IBM Granite)
- **Purpose:** End-to-end document understanding with vision models
- **Model:** IBM Granite Docling (258M parameters)
- **Speed:**
  - **CPU:** 30-60+ minutes per document
  - **GPU:** 2-5 minutes per document (10-20x faster)
- **Use Case:** Complex documents with diagrams, tables, mixed layouts
- **Resource Usage:** Very High
  - **CPU:** 7-8 GB RAM, 300%+ CPU (multi-core)
  - **GPU:** 4-6 GB VRAM, significantly faster

---

## Performance Benchmarks

### Tested Documents
- **SFTR Regulation:** 34 pages, 1 table, 910 KB
- **SFTR Delegated Regulation:** 21 pages, 22 tables, 490 KB

### Processing Times (CPU-only, 16 cores)

| Mode | SFTR Reg (34p) | SFTR Del (21p) | Avg Speed |
|------|----------------|----------------|-----------|
| QUICK | 161s (2.7 min) | 199s (3.3 min) | 0.15 pages/sec |
| SLOW | 54s (0.9 min) | ~60s (est.) | 0.50 pages/sec |
| ACCURATE | ~60s (est.) | ~70s (est.) | 0.45 pages/sec |
| VLM | 1800s+ (30+ min) | 2400s+ (40+ min) | 0.02 pages/sec |

**Note:** VLM mode would be 10-20x faster with GPU acceleration.

---

## Troubleshooting

### Issue: Tesseract OCR Not Working

**Error:** `tesserocr is not correctly configured`

**Solution:**
```bash
# Install Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Set environment variable
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Verify
ls $TESSDATA_PREFIX/eng.traineddata
```

### Issue: Out of Memory During VLM Processing

**Error:** Process killed or `OutOfMemoryError`

**Solutions:**
1. **Increase available RAM** (16 GB minimum for VLM)
2. **Process one document at a time** (modify script)
3. **Use GPU** instead of CPU (10-20x less memory on GPU)
4. **Skip VLM mode** if not critical

### Issue: CUDA Not Available

**Check:**
```bash
.venv/bin/python -c "import torch; print(torch.cuda.is_available())"
```

**If False:**
1. Check if NVIDIA GPU is installed: `nvidia-smi`
2. Reinstall PyTorch with CUDA: `uv pip install torch --index-url https://download.pytorch.org/whl/cu118`
3. Verify CUDA version matches PyTorch

### Issue: Slow Processing

**Optimization Tips:**
1. **Use QUICK mode** for text-based PDFs (skip OCR)
2. **Enable GPU** for VLM mode (10-20x speedup)
3. **Process in parallel** (already implemented in script)
4. **Use SSD** instead of HDD for I/O operations

### Issue: Package Installation Fails

**Error:** `Failed to build` or dependency conflicts

**Solution:**
```bash
# Clear cache and reinstall
rm -rf .venv
rm uv.lock
uv sync
```

---

## Environment Variables Reference

```bash
# Required for OCR modes
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Optional: Control number of threads
export OMP_NUM_THREADS=8

# Optional: Limit PyTorch CPU threads
export TORCH_NUM_THREADS=8

# Optional: Disable GPU (force CPU)
export CUDA_VISIBLE_DEVICES=""
```

---

## Verification Checklist

After setup, verify everything is working:

- [ ] Python 3.9-3.12 installed
- [ ] `uv` package manager installed
- [ ] Virtual environment created (`.venv/` exists)
- [ ] All dependencies installed (`uv sync` completed)
- [ ] Tesseract installed and language data present
- [ ] `TESSDATA_PREFIX` environment variable set
- [ ] Can import docling: `.venv/bin/python -c "import docling; print(docling.__version__)"`
- [ ] Can check CUDA: `.venv/bin/python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Scripts are executable: `chmod +x run_all_modes.sh`

---

## Quick Start Commands

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone <repo-url>
cd NYQSTdocling
uv sync

# 3. Install Tesseract (Linux)
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# 4. Set environment
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# 5. Run processing
./run_all_modes.sh
```

---

## Additional Resources

- **Docling Documentation:** https://docling-project.github.io/docling/
- **Docling GitHub:** https://github.com/docling-project/docling
- **IBM Granite Model:** https://huggingface.co/ibm-granite/granite-docling-258M
- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **uv Package Manager:** https://github.com/astral-sh/uv

---

**Document Version:** 1.0
**Last Updated:** 2025-11-26
**Environment:** Linux x86_64, CPU-only, 16 cores, 13GB RAM
