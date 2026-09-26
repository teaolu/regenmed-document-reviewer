# RegenMed Internal Document Reviewer — Free Starter

This starter uses no paid AI API and needs no API key.

## What this first version does

- Uploads one PDF
- Converts PDF pages to images
- Runs local Tesseract OCR
- Detects:
  - MP-F-023
  - QS-F-049
  - Lot Log / MP-F-021
  - Discard Form / MP-F-018
- Shows a preview and OCR text

Field-level validation is intentionally the next step after deployment is confirmed.

## Free stack

- Streamlit
- PyMuPDF
- OpenCV
- Tesseract OCR
- Python

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload all files from this project to the repository root.
3. Open Streamlit Community Cloud.
4. Create a new app from the repository.
5. Main file path: `app.py`
6. Deploy.

There are no secrets and no API keys to configure.

`packages.txt` tells Streamlit Cloud to install the system-level Tesseract OCR package.
