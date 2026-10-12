import streamlit as st

from src.application.use_cases import AnalyzeDocumentUseCase
from src.config.settings import Settings
from src.infrastructure.azure_analyzer import AzureDocumentAnalyzer
from src.presentation.components import (
    analyze_button,
    apply_styles,
    file_uploader,
    model_selector,
    show_preview,
)
from src.presentation.tables import render_tables

st.set_page_config(page_title="Azure Document Intelligence", layout="wide")
apply_styles()

PANEL_HEIGHT = 800


@st.cache_resource
def get_use_case() -> AnalyzeDocumentUseCase:
    """Composition root: wire the Azure adapter into the use case."""
    analyzer = AzureDocumentAnalyzer(Settings.load())
    return AnalyzeDocumentUseCase(analyzer)


def main() -> None:
    st.title("Azure AI Document Intelligence")

    try:
        use_case = get_use_case()
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    # ---- controls (full width) ----
    top_left, top_right = st.columns(2)
    with top_left:
        model = model_selector()
    with top_right:
        uploaded = file_uploader()

    if uploaded is None:
        st.session_state.pop("results", None)
        st.info("Select a model and upload a document to begin.")
        st.stop()

    file_bytes = uploaded.getvalue()
    result_key = (uploaded.name, model.model_id)

    if analyze_button(disabled=False):
        with st.spinner(f"Analyzing with {model.label}..."):
            try:
                views = use_case.execute(file_bytes, model)
                st.session_state["results"] = {"key": result_key, "views": views}
            except (RuntimeError, ValueError) as exc:
                st.session_state.pop("results", None)
                st.error(str(exc))

    # ---- side by side: document | results ----
    doc_col, result_col = st.columns(2, gap="large")

    with doc_col:
        with st.container(height=PANEL_HEIGHT, border=True):
            show_preview(uploaded.name, file_bytes)

    with result_col:
        with st.container(height=PANEL_HEIGHT, border=True):
            saved = st.session_state.get("results")
            if saved and saved["key"] == result_key:
                render_tables(saved["views"])
            else:
                st.subheader("Results")
                st.caption("Click **Analyze Document** to see the results here.")


if __name__ == "__main__":
    main()