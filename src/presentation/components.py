import io

import fitz  # pymupdf
import streamlit as st
from PIL import Image

from src.domain.entities import AnalysisModel

SUPPORTED_TYPES = ["pdf", "png", "jpg", "jpeg", "bmp", "tiff", "tif"]
MAX_PREVIEW_PAGES = 5


def model_selector() -> AnalysisModel:
    """Dropdown with the 5 prebuilt models."""
    return st.selectbox(
        "1. Select model",
        options=list(AnalysisModel),
        format_func=lambda model: model.label,
    )


def file_uploader():
    """File upload widget. Returns the uploaded file or None."""
    return st.file_uploader("2. Upload a document", type=SUPPORTED_TYPES)


def show_preview(file_name: str, file_bytes: bytes) -> None:
    """Show the uploaded document: images directly, PDFs as rendered pages."""
    st.subheader("Document preview")

    if file_name.lower().endswith(".pdf"):
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            total = len(pdf)
            for index in range(min(total, MAX_PREVIEW_PAGES)):
                pixmap = pdf[index].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                st.image(
                    pixmap.tobytes("png"),
                    caption=f"Page {index + 1} of {total}",
                )
            if total > MAX_PREVIEW_PAGES:
                st.caption(f"Preview shows the first {MAX_PREVIEW_PAGES} pages only.")
    else:
        # Convert to PNG so formats like TIFF display in the browser
        image = Image.open(io.BytesIO(file_bytes))
        st.image(image, caption=file_name)


def analyze_button(disabled: bool) -> bool:
    """Returns True on the run when the button is clicked."""
    return st.button(
        "3. Analyze Document",
        type="primary",
        disabled=disabled,
    )

def apply_styles() -> None:
    """Bigger fonts for the whole app, including the result tables."""
    st.markdown(
        """
        <style>
        .stApp p, .stApp label, .stApp li, .stApp span,
        .stApp div[data-baseweb="select"] * {
            font-size: 1.15rem;
        }
        [data-testid="stTable"] table,
        [data-testid="stTable"] th,
        [data-testid="stTable"] td {
            font-size: 1.15rem !important;
        }
        [data-testid="stTable"] td, [data-testid="stTable"] th {
            padding: 0.6rem 0.8rem !important;
        }
        [data-testid="stTable"] {
            overflow-x: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )