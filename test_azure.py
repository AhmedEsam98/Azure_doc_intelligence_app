from src.config.settings import Settings
from src.domain.entities import AnalysisModel
from src.infrastructure.azure_analyzer import AzureDocumentAnalyzer

PATH = r"D:\Anime\chat_with_cvs\data\(Sherif Ashraf CV).pdf"

analyzer = AzureDocumentAnalyzer(Settings.load())

with open(PATH, "rb") as f:
    result = analyzer.analyze(f.read(), AnalysisModel.READ)

print(len(result.pages), "page(s);", sum(len(p.lines) for p in result.pages), "lines")