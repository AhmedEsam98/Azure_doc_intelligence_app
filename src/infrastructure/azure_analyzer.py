from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from src.config.settings import Settings
from src.domain.entities import (
    AnalysisModel,
    AnalysisResult,
    ExtractedField,
    ExtractedTable,
    KeyValuePair,
    PageContent,
)
from src.domain.interfaces import DocumentAnalyzer


class AzureDocumentAnalyzer(DocumentAnalyzer):
    """Adapter: Azure AI Document Intelligence -> domain entities."""

    def __init__(self, settings: Settings):
        self._client = DocumentAnalysisClient(
            endpoint=settings.endpoint,
            credential=AzureKeyCredential(settings.key),
        )

    def analyze(self, file_bytes: bytes, model: AnalysisModel) -> AnalysisResult:
        try:
            poller = self._client.begin_analyze_document(
                model_id=model.model_id,
                document=file_bytes,
            )
            azure_result = poller.result()
        except HttpResponseError as exc:
            raise RuntimeError(f"Azure analysis failed: {exc.message}") from exc

        result = AnalysisResult(model=model)
        self._map_documents(azure_result, result)
        self._map_key_value_pairs(azure_result, result)
        self._map_tables(azure_result, result)
        self._map_pages(azure_result, result)
        return result

    # ---------- mapping helpers ----------

    @staticmethod
    def _field_text(field) -> str:
        """Readable text for any Azure field (prefer the raw text found)."""
        if field is None:
            return ""
        if field.content:
            return field.content
        return "" if field.value is None else str(field.value)

    def _map_documents(self, azure_result, result: AnalysisResult) -> None:
        """Invoice / Receipt: named fields + line items."""
        for document in azure_result.documents or []:
            for name, field in document.fields.items():
                if field.value_type == "list":
                    # e.g. "Items": a list of dictionaries -> line items
                    for item in field.value or []:
                        if item.value_type == "dictionary":
                            result.line_items.append(
                                {
                                    sub_name: self._field_text(sub_field)
                                    for sub_name, sub_field in item.value.items()
                                }
                            )
                elif field.value_type == "dictionary":
                    continue  # nested objects are skipped to keep the table flat
                else:
                    result.fields.append(
                        ExtractedField(
                            name=name,
                            value=self._field_text(field),
                            confidence=field.confidence,
                        )
                    )

    def _map_key_value_pairs(self, azure_result, result: AnalysisResult) -> None:
        """General Document: detected key/value pairs."""
        for pair in azure_result.key_value_pairs or []:
            result.key_value_pairs.append(
                KeyValuePair(
                    key=pair.key.content if pair.key else "",
                    value=pair.value.content if pair.value else "",
                    confidence=pair.confidence,
                )
            )

    def _map_tables(self, azure_result, result: AnalysisResult) -> None:
        """Layout / General Document: tables as a grid of text."""
        for table in azure_result.tables or []:
            grid = [["" for _ in range(table.column_count)] for _ in range(table.row_count)]
            for cell in table.cells:
                grid[cell.row_index][cell.column_index] = cell.content
            page_number = table.bounding_regions[0].page_number if table.bounding_regions else 1
            result.tables.append(ExtractedTable(page_number=page_number, rows=grid))

    def _map_pages(self, azure_result, result: AnalysisResult) -> None:
        """Read / Layout / General Document: text lines per page."""
        for page in azure_result.pages or []:
            result.pages.append(
                PageContent(
                    page_number=page.page_number,
                    lines=[line.content for line in page.lines or []],
                )
            )