from abc import ABC, abstractmethod

from src.domain.entities import AnalysisModel, AnalysisResult


class DocumentAnalyzer(ABC):
    """Contract for any service that can analyze a document.

    The application layer depends on this interface, not on Azure.
    """

    @abstractmethod
    def analyze(self, file_bytes: bytes, model: AnalysisModel) -> AnalysisResult:
        ...