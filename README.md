# RegenMed Internal Document Reviewer — Free Version 2

No paid AI API. No API key.

## Version 2 milestone

- PDF upload
- Local Tesseract OCR
- Form classification
- MP-F-023 computer-vision validation:
  - top required fields
  - By/Date initials and date presence
  - Operations Manager Review
  - Produced and Packaged processing cells

QS-F-049 and Lot Log validators are the next milestones.

## Updating an existing Streamlit deployment

Replace/add the files in the GitHub repository:
- app.py
- document_reader.py
- mp023_validator.py
- requirements.txt
- packages.txt

Commit the changes. Streamlit Community Cloud should rebuild the app from GitHub.

## Important

This version uses normalized form coordinates because the hackathon forms have known layouts.
It is intended for unseen filled-out copies of the same MP-F-023 template, not arbitrary documents.
