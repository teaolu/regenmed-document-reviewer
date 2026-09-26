from io import BytesIO

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image


def render_pdf_pages(pdf_bytes: bytes, zoom: float = 2.0):
    """Render every PDF page to a PIL RGB image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    matrix = fitz.Matrix(zoom, zoom)

    for page in doc:
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(image)

    if not pages:
        raise ValueError("The PDF contains no pages.")

    return pages


def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """Improve contrast for printed-text OCR."""
    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        12,
    )
    return Image.fromarray(binary)


def ocr_image(image: Image.Image) -> str:
    processed = preprocess_for_ocr(image)
    return pytesseract.image_to_string(processed, config="--psm 6")


def detect_form_type(text: str):
    """
    Detect the form from printed headings/form codes rather than the filename.
    Returns (form_type, explanation).
    """
    t = " ".join(text.upper().split())

    checks = [
        ("MP-F-023", ["MS PROCESSING INSTRUCTIONS", "TISSUE OPEN CHECKLIST", "MP-F-023"]),
        ("QS-F-049", ["TECHNICAL/QUALITY REVIEW", "DISPOSITION STATEMENT", "QS-F-049"]),
        ("LOT_LOG", ["MP-F-021", "PACKAGING", "REGENMED ITEM"]),
        ("DISCARD_FORM", ["TISSUE DISCARD FORM", "MP-F-018", "REASON FOR DISCARD"]),
    ]

    scores = {}
    for form_type, keywords in checks:
        scores[form_type] = sum(1 for keyword in keywords if keyword in t)

    best_form = max(scores, key=scores.get)
    best_score = scores[best_form]

    if best_score == 0:
        return "UNKNOWN", "No expected printed heading or form code was confidently recognized."

    return best_form, f"Detected from printed text/form-code matches (score {best_score})."
