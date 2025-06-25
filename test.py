import fitz  # PyMuPDF
from gmft.auto import AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document
import os
from tqdm import tqdm
from joblib import Memory
import pandas as pd

memory = Memory(location=".gmft_cache", verbose=0)

@memory.cache
def get_detector():
    return AutoTableDetector()

@memory.cache
def get_formatter():
    return AutoTableFormatter()

DPI = 150
detector = get_detector()
formatter = get_formatter()

def is_page_searchable(page, min_chars=10):
    text = page.get_text().strip()
    return len(text) >= min_chars

def has_tables(pdf_path, page_number):
    doc = PyPDFium2Document(pdf_path)
    try:
        page = doc[page_number]
        table_regions = list(detector.extract(page))
        return len(table_regions) > 0
    finally:
        doc.close()

def ocr_page(page, page_number):
    pix = page.get_pixmap(dpi=DPI)
    imgpdf = fitz.open("pdf", pix.pdfocr_tobytes())
    temp_path = f"temp_page_{page_number+1}.pdf"
    imgpdf.save(temp_path)
    imgpdf.close()
    return temp_path

def extract_tables_from_page(pdf_path, page_number):
    doc = PyPDFium2Document(pdf_path)
    page_tables = []
    table_boxes = []
    try:
        page = doc[page_number]
        for cropped in detector.extract(page):
            table_boxes.append(cropped.bbox)
            formatted = formatter.extract(cropped, margin='auto', padding=None)
            df = formatted.df()
            page_tables.append((cropped.bbox, df))
    finally:
        doc.close()
    return page_tables

def extract_text_excluding_tables(page, table_boxes):
    clean_text = ""
    blocks = page.get_text("blocks")  # List of (x0, y0, x1, y1, "text", block_no, block_type, block_flags)

    for block in blocks:
        x0, y0, x1, y1, text = block[:5]
        block_rect = fitz.Rect(x0, y0, x1, y1)
        is_overlapping = any(fitz.Rect(*box).intersects(block_rect) for box in table_boxes)
        if not is_overlapping:
            clean_text += text.strip() + "\n"
    return clean_text.strip()

def smart_pdf_processing_with_text_and_tables(input_pdf, ocr_output_pdf):
    src = fitz.open(input_pdf)
    ocr_doc = fitz.open()
    full_output = ""

    for i, page in enumerate(src, start=0):
        print(f"\n📄 Page {i + 1}")

        searchable = is_page_searchable(page)
        table_exists = has_tables(input_pdf, i)

        print(f"   🧠 Searchable: {'✅ Yes' if searchable else '❌ No'}")
        print(f"   📊 Tables: {'✅ Yes' if table_exists else '❌ No'}")

        if not table_exists and not searchable:
            continue

        if not searchable:
            temp_path = ocr_page(page, i)
            temp_doc = fitz.open(temp_path)
            ocr_page_obj = temp_doc[0]
            page_tables = extract_tables_from_page(temp_path, 0)
            table_boxes = [box for box, _ in page_tables]
            text_content = extract_text_excluding_tables(ocr_page_obj, table_boxes)

            # Merge to ocr_doc for saving later
            ocr_doc.insert_pdf(temp_doc)
            temp_doc.close()
            os.remove(temp_path)
        else:
            page_tables = extract_tables_from_page(input_pdf, i)
            table_boxes = [box for box, _ in page_tables]
            text_content = extract_text_excluding_tables(page, table_boxes)

        # Write text
        if text_content.strip():
            full_output += f"\n--- Page {i + 1} ---\n\n{text_content}\n"

        # Write tables
        for j, (bbox, df) in enumerate(page_tables, 1):
            table_csv_name = f"table_page{i+1}_{j}.csv"
            full_output += f"\n[Table Page {i+1}.{j}]\n"
            full_output += df.to_markdown(index=False) + "\n"

    if len(ocr_doc) > 0:
        ocr_doc.save(ocr_output_pdf)
        print(f"\n💾 OCR-enhanced pages saved to: {ocr_output_pdf}")

    ocr_doc.close()
    src.close()

    # Save the full document (text + tables)
    with open("document_output.md", "w", encoding="utf-8") as f:
        f.write(full_output)
    print("\n📄 Combined document saved as: document_output.md")

    return full_output


input_pdf = r"sample_pdf\Shell - Financial Statement-Page1-5 1.pdf"
ocr_output_pdf = "input-ocr.pdf"
# Run the pipeline
tables = smart_pdf_processing_with_text_and_tables(input_pdf, ocr_output_pdf)
print(f"\n✅ Total tables extracted: {len(tables)}")
