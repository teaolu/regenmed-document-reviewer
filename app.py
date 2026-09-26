import streamlit as st

from document_reader import render_pdf_pages, detect_form_type, ocr_image
from mp023_validator import validate_mp023

st.set_page_config(
    page_title="RegenMed Internal Document Reviewer",
    page_icon="📄",
    layout="wide",
)

st.title("RegenMed Internal Document Reviewer")
st.caption("Free prototype: local OCR + computer vision + deterministic Python rules.")

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

st.subheader("Detected form")
if form_type == "UNKNOWN":
    st.error("Unknown form type")
else:
    st.success(form_type)
st.caption(reason)

if form_type == "MP-F-023":
    with st.spinner("Checking MP-F-023 required fields..."):
        result = validate_mp023(first_page)

    st.subheader("Review result")

    if result["passed"]:
        st.success("No missing MP-F-023 fields were detected by the current checks.")
    else:
        st.error(f"{len(result['issues'])} issue(s) found")
        for i, issue in enumerate(result["issues"], start=1):
            with st.container(border=True):
                st.markdown(f"**{i}. {issue['location']}**")
                st.write(issue["message"])

    st.caption(
        "This is a computer-vision prototype. A flagged field means the writable area "
        "appears blank; final human review still remains appropriate."
    )

    with st.expander("Developer view: field occupancy scores"):
        st.dataframe(result["debug"], use_container_width=True, hide_index=True)

elif form_type in {"QS-F-049", "LOT_LOG", "DISCARD_FORM"}:
    st.info(
        f"{form_type} classification is working. "
        "We are adding its field-level validation after MP-F-023 is tested."
    )

with st.expander("Preview first page"):
    st.image(first_page, use_container_width=True)

with st.expander("Developer view: OCR text"):
    st.text(first_page_text)
