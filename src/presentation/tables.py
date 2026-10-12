import re

import pandas as pd
import streamlit as st

from src.application.mappers import TableView


def _to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def _file_name(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return f"{slug or 'table'}.csv"


def render_tables(views: list[TableView]) -> None:
    """Render each table with its title, size, and a CSV download button."""
    st.subheader("Results")

    if not views:
        st.info("No structured data was found for this model and document.")
        return

    for index, view in enumerate(views):
        st.markdown(f"### {view.title}")
        st.caption(f"{len(view.data)} rows × {len(view.data.columns)} columns")

        table = view.data.copy()
        table.index = range(1, len(table) + 1)  # start row numbers at 1
        st.table(table)

        st.download_button(
            "Download CSV",
            data=_to_csv(view.data),
            file_name=_file_name(view.title),
            mime="text/csv",
            key=f"download_{index}",
        )