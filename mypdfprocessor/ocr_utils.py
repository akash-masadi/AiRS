# mypdfprocessor/ocr_utils.py
import pytesseract
import numpy as np
from pdf2image import convert_from_path

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    text = text.strip()
    if text != '':
        return text
    return ''

def extract_text(pdf_file):
    pages = convert_from_path(pdf_file)
    extracted_text = []
    for page in pages:
        text = extract_text_from_image(page)
        extracted_text.append(text)
    extracted_text = "\n".join(extracted_text) 
    return extracted_text
