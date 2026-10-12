from src.application.use_cases import AnalyzeDocumentUseCase
from src.domain.entities import AnalysisModel, AnalysisResult, ExtractedField
from src.domain.interfaces import DocumentAnalyzer


class FakeAnalyzer(DocumentAnalyzer):
    def analyze(self, file_bytes, model):
        return AnalysisResult(
            model=model,
            fields=[ExtractedField("VendorName", "Contoso", 0.98)],
            line_items=[{"Description": "Pen", "Amount": "5"}],
        )


views = AnalyzeDocumentUseCase(FakeAnalyzer()).execute(b"x", AnalysisModel.INVOICE)
for view in views:
    print(view.title)
    print(view.data)