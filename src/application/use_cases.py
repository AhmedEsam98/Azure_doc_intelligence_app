from src.application.mappers import TableView, map_result
from src.domain.entities import AnalysisModel
from src.domain.interfaces import DocumentAnalyzer


class AnalyzeDocumentUseCase:
    """Analyze a document with the chosen model and return display-ready tables."""

    def __init__(self, analyzer: DocumentAnalyzer):
        self._analyzer = analyzer

    def execute(self, file_bytes: bytes, model: AnalysisModel) -> list[TableView]:
        if not file_bytes:
            raise ValueError("The uploaded file is empty.")
        result = self._analyzer.analyze(file_bytes, model)
        return map_result(result)