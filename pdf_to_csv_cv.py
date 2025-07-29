import os
import csv
import math
import cv2
import numpy as np
import pytesseract
import argparse
import fitz 
from imutils.perspective import four_point_transform
from imutils.contours import sort_contours

DEBUG = False
ROW_MIN_HEIGHT = 5
COLUMN_MIN_WIDTH = 5
PADDING = 2

def extract_with_opencv_ocr(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    csv_output_path = os.path.join(output_dir, f"{pdf_name}_scanned.csv")
    doc = fitz.open(pdf_path)

    with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for page_num in range(len(doc)):
            print(f"🖼️ Processing page {page_num+1}")
            pix = doc.load_page(page_num).get_pixmap(dpi=300)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))

            if pix.n == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            extracted_table = extract_main_table(img)
            if extracted_table is None:
                print(f"⚠️ Skipping page {page_num+1} — no usable contours found")
                continue

            row_images = extract_rows_columns(extracted_table)
            for idx, row in enumerate(row_images, start=1):
                config = "-l eng --oem 1 --psm 7"
                row_texts = [pytesseract.image_to_string(col, config=config) for col in row]
                cleaned_row = [cell.strip() for cell in row_texts if cell.strip()]
                if cleaned_row:
                    print(f"🧹 Cleaned row {idx}: {cleaned_row}")
                    csv_writer.writerow(cleaned_row)

    print(f"\n📦 Saved scanned content to: {csv_output_path}")

def extract_main_table(gray_image):
    inverted = cv2.bitwise_not(gray_image)
    blurred = cv2.GaussianBlur(inverted, (5, 5), 0)
    thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    valid_cnts = [c for c in cnts if c is not None and len(c) > 0 and c.dtype in [np.int32, np.float32]]
    if not valid_cnts:
        return None

    cnts = sorted(valid_cnts, key=cv2.contourArea, reverse=True)
    rect = cv2.minAreaRect(cnts[0])
    box = cv2.boxPoints(rect)
    box = box.astype(np.intp)
    extracted = four_point_transform(gray_image.copy(), box.reshape(4, 2))
    return extracted

def horizontal_boxes_filter(box, width):
    return box[2] > width * 0.7

def vertical_boxes_filter(box, height):
    return box[3] > height * 0.7

def extract_rows_columns(gray_image):
    inverted = cv2.bitwise_not(gray_image)
    blurred = cv2.GaussianBlur(inverted, (5, 5), 0)
    height, width = gray_image.shape
    thresholded = cv2.threshold(blurred, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, math.ceil(height * 0.2)))
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (math.ceil(width * 0.2), 1))

    vertical_lines_img = cv2.dilate(cv2.erode(thresholded, vertical_kernel, iterations=2), vertical_kernel, iterations=2)
    horizontal_lines_img = cv2.dilate(cv2.erode(thresholded, hori_kernel, iterations=2), hori_kernel, iterations=2)

    vertical_contours, _ = cv2.findContours(vertical_lines_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    horizontal_contours, _ = cv2.findContours(horizontal_lines_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vertical_contours, v_boxes = sort_contours(vertical_contours, method="left-to-right")
    horizontal_contours, h_boxes = sort_contours(horizontal_contours, method="top-to-bottom")

    v_boxes = list(filter(lambda x: vertical_boxes_filter(x, height), v_boxes))
    h_boxes = list(filter(lambda x: horizontal_boxes_filter(x, width), h_boxes))

    if DEBUG:
        overlay = cv2.cvtColor(gray_image.copy(), cv2.COLOR_GRAY2BGR)
        for box in h_boxes + v_boxes:
            x, y, w, h = box
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)
        show_wait_destroy("Detected Table Lines", overlay)

    extracted_rows_columns = []
    for idx_h in range(1, len(h_boxes)):
        hy_p = h_boxes[idx_h - 1][1]
        hy_c = h_boxes[idx_h][1]
        hh_c = h_boxes[idx_h][3]

        row = []
        for idx_v in range(1, len(v_boxes)):
            vx_p = v_boxes[idx_v - 1][0]
            vx_c = v_boxes[idx_v][0]
            vw_c = v_boxes[idx_v][2]

            cell = gray_image[hy_p:hy_c + hh_c, vx_p:vx_c + vw_c]
            blurred = cv2.GaussianBlur(cell, (5, 5), 0)
            thresholded = cv2.threshold(blurred, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            contours = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            if contours:
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                rect = cv2.minAreaRect(contours[0])
                box = cv2.boxPoints(rect)
                box = box.astype(np.intp)
                extracted = four_point_transform(cell.copy(), box.reshape(4, 2))[1:-1, 1:-1]
                extracted = cv2.threshold(extracted, 165, 255, cv2.THRESH_BINARY)[1]
                row.append(extracted)

        if row:
            extracted_rows_columns.append(row)

    return extracted_rows_columns

def show_wait_destroy(winname, img):
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.imshow(winname, img)
    cv2.resizeWindow(winname, 1000, 800)
    cv2.moveWindow(winname, 500, 0)
    cv2.waitKey(0)
    cv2.destroyWindow(winname)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--pdf", type=str, nargs="+", required=True, help="Path to input PDF(s)")
    ap.add_argument("-o", "--output_dir", type=str, default="outputs", help="Directory to save output CSVs")
    args = vars(ap.parse_args())

    for file_path in args["pdf"]:
        extract_with_opencv_ocr(file_path, args["output_dir"])
