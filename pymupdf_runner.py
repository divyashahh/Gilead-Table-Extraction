import fitz  # PyMuPDF
import os
import csv

def extract_text_from_pdf(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    combined_csv_path = os.path.join(output_dir, f"{pdf_name}_digital.csv")

    doc = fitz.open(pdf_path)

    with open(combined_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Page", "Text"])

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_lines = page.get_text("text").splitlines()

            for line in text_lines:
                writer.writerow([f"Page {page_num+1}", line])

            print(f"✅ Extracted page {page_num+1}")

    print(f"\n📦 Saved digital content to: {combined_csv_path}")
