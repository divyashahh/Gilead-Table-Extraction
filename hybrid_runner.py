import os
import argparse
from PyPDF2 import PdfReader
from pdf_to_csv_cv import extract_with_opencv_ocr  
from pymupdf_runner import extract_text_from_pdf

def is_pdf_scanned(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            if page.extract_text():
                return False  # Text found → digital
        return True  # No extractable text → scanned
    except Exception as e:
        print(f"⚠️ Error analyzing PDF: {e}")
        return True

def run_pipeline(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    if is_pdf_scanned(pdf_path):
        print("🖼️ Detected scanned PDF — using OCR")
        extract_with_opencv_ocr(pdf_path, output_dir)
    else:
        print("📄 Detected digital PDF — using PyMuPDF (full text)")
        extract_text_from_pdf(pdf_path, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pdf_path", type=str, required=True, help="Path to input PDF file")
    parser.add_argument("-o", "--output_dir", type=str, default="outputs", help="Directory to save outputs")
    args = parser.parse_args()

    run_pipeline(args.pdf_path, args.output_dir)


