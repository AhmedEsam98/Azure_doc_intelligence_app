from dataclasses import dataclass
from typing import Callable

import pandas as pd

from src.domain.entities import AnalysisModel, AnalysisResult


@dataclass(frozen=True)
class TableView:
    """A titled table, ready for the UI to render."""

    title: str
    data: pd.DataFrame


# ---------- small helpers ----------

def _fields_table(result: AnalysisResult) -> list[TableView]:
    if not result.fields:
        return []
    df = pd.DataFrame(
        [
            {
                "Field": f.name,
                "Value": f.value,
                "Confidence": round(f.confidence, 2) if f.confidence is not None else None,
            }
            for f in result.fields
        ]
    )
    return [TableView("Extracted Fields", df)]


def _line_items_table(result: AnalysisResult) -> list[TableView]:
    if not result.line_items:
        return []
    return [TableView("Line Items", pd.DataFrame(result.line_items).fillna(""))]


def _key_value_table(result: AnalysisResult) -> list[TableView]:
    if not result.key_value_pairs:
        return []
    df = pd.DataFrame(
        [
            {
                "Key": p.key,
                "Value": p.value,
                "Confidence": round(p.confidence, 2) if p.confidence is not None else None,
            }
            for p in result.key_value_pairs
        ]
    )
    return [TableView("Key-Value Pairs", df)]


def _document_tables(result: AnalysisResult) -> list[TableView]:
    views = []
    for index, table in enumerate(result.tables, start=1):
        rows = table.rows
        header = rows[0] if rows else []
        use_header = (
            len(rows) > 1
            and all(h.strip() for h in header)
            and len(set(header)) == len(header)
        )
        if use_header:
            df = pd.DataFrame(rows[1:], columns=header)
        else:
            df = pd.DataFrame(rows)
        views.append(TableView(f"Table {index} (page {table.page_number})", df))
    return views


def _lines_table(result: AnalysisResult) -> list[TableView]:
    rows = [
        {"Page": page.page_number, "Line": number, "Text": text}
        for page in result.pages
        for number, text in enumerate(page.lines, start=1)
    ]
    if not rows:
        return []
    return [TableView("Text Lines", pd.DataFrame(rows))]


# ---------- one mapper per model ----------

def _map_invoice(result: AnalysisResult) -> list[TableView]:
    return _fields_table(result) + _line_items_table(result)


def _map_receipt(result: AnalysisResult) -> list[TableView]:
    return _fields_table(result) + _line_items_table(result)


def _map_read(result: AnalysisResult) -> list[TableView]:
    return _lines_table(result)


def _map_layout(result: AnalysisResult) -> list[TableView]:
    return _document_tables(result) + _lines_table(result)


def _map_general_document(result: AnalysisResult) -> list[TableView]:
    return _key_value_table(result) + _document_tables(result) + _lines_table(result)


_MAPPERS: dict[AnalysisModel, Callable[[AnalysisResult], list[TableView]]] = {
    AnalysisModel.INVOICE: _map_invoice,
    AnalysisModel.RECEIPT: _map_receipt,
    AnalysisModel.READ: _map_read,
    AnalysisModel.LAYOUT: _map_layout,
    AnalysisModel.GENERAL_DOCUMENT: _map_general_document,
}


def map_result(result: AnalysisResult) -> list[TableView]:
    """Pick the right mapper for the result's model."""
    return _MAPPERS[result.model](result)