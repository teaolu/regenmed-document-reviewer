import streamlit as st
from document_reader import render_pdf_pages, detect_form_type, ocr_image

st.set_page_config(
    page_title="RegenMed Internal Document Reviewer",
    page_icon="📄",
    layout="wide",
)

st.title("RegenMed Internal Document Reviewer")
st.caption("Free prototype: PDF rendering + local OCR + Python rules. No paid AI API.")

uploaded = st.file_uploader(
    "Upload one RegenMed PDF",
    type=["pdf"],
    accept_multiple_files=False,
)

if uploaded is None:
    st.info("Upload a PDF to begin.")
    st.stop()

pdf_bytes = uploaded.getvalue()

try:
    pages = render_pdf_pages(pdf_bytes)
except Exception as exc:
    st.error(f"Could not open the PDF: {exc}")
    st.stop()

first_page = pages[0]
with st.spinner("Reading the form..."):
    first_page_text = ocr_image(first_page)
    form_type, reason = detect_form_type(first_page_text)

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Preview")
    st.image(first_page, use_container_width=True)

with right:
    st.subheader("Detected form")
    if form_type == "UNKNOWN":
        st.error("Unknown form type")
    else:
        st.success(form_type)

    st.caption(reason)
    st.write(f"Pages detected: **{len(pages)}**")

    st.subheader("Current prototype status")
    st.write(
        "✅ PDF upload works\n\n"
        "✅ PDF pages are converted to images\n\n"
        "✅ OCR runs locally on the deployed app\n\n"
        "✅ Form type detection is enabled\n\n"
        "🛠 Field-by-field validation is the next build step"
    )

with st.expander("Developer view: OCR text"):
    st.text(first_page_text)
