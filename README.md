# 📄 Table Extraction Pipeline

This project automates table extraction from both **scanned image-based PDFs** and **digital text PDFs**, converting structured content into clean CSV files.

## ✅ Features

- 🔍 Automatically detects if the PDF is scanned or digital
- 📦 Extracts tables only — ignores headers and body paragraphs (scanned flow)
- 🧠 Uses PyMuPDF (`fitz`) for PDF rendering (no Poppler needed)
- 🖼️ Applies OpenCV-based table detection for scanned pages
- 🗣️ Runs Tesseract OCR on cropped table cells
- 🧹 Cleans noisy output with filtering and post-processing

---

## 🧠 How It Works

### Scanned PDFs:
- Pages are rendered into high-res grayscale images using PyMuPDF
- Table boundaries are detected via OpenCV (`cv2.findContours`, kernel filters)
- Each table cell is extracted, cleaned, and passed to Tesseract OCR
- Output is written to:  
  `outputs/<filename>_scanned.csv`

### Digital PDFs:
- Currently uses PyMuPDF to extract full-page text
- (Optional) Can be enhanced with block-level heuristics for table-only filtering
- Output is written to:  
  `outputs/<filename>_digital.csv`

---

## 🚀 How to Run

Make sure your input PDF (e.g. `test.pdf`) is inside the `inputs/` folder. Then run:

```bash
python hybrid_runner.py -p inputs/test.pdf -o outputs

```

The script auto-selects the proper extraction path based on whether the input is scanned or digital.

---

## ⚙️ Dependencies

This pipeline is free from system-level binaries like Poppler — just install dependencies via pip:

```bash
pip install opencv-python pytesseract numpy PyMuPDF imutils
```

Make sure Tesseract is installed locally and accessible via system path.

---

## 🧪 Debugging & Tuning

Set `DEBUG = True` inside `pdf_to_csv_cv.py` to visualize detected table areas and diagnose misaligned contours.
