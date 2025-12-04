#!/bin/bash
# Run SFTR/ESMA document processing with all modes enabled

# Set Tesseract data path for OCR modes
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Clean previous partial outputs
rm -rf output/slow output/accurate output/vlm

# Run the processing script
.venv/bin/python process_sftr_esma_v2.py 2>&1 | tee processing_full_run.log

echo ""
echo "Processing complete! Check output/ directory for results."
