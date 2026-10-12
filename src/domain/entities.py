from dataclasses import dataclass, field
from enum import Enum


class AnalysisModel(Enum):
    """The prebuilt models the user can choose from."""

    INVOICE = ("Prebuilt Invoice", "prebuilt-invoice")
    RECEIPT = ("Prebuilt Receipt", "prebuilt-receipt")
    READ = ("Prebuilt Read", "prebuilt-read")
    LAYOUT = ("Prebuilt Layout", "prebuilt-layout")
    GENERAL_DOCUMENT = ("Prebuilt General Document", "prebuilt-document")

    def __init__(self, label: str, model_id: str):
        self.label = label
        self.model_id = model_id


@dataclass(frozen=True)
class ExtractedField:
    """A named value, e.g. VendorName = 'Contoso' (invoice/receipt)."""

    name: str
    value: str
    confidence: float | None = None


@dataclass(frozen=True)
class KeyValuePair:
    """A key/value pair detected in the document (general document)."""

    key: str
    value: str
    confidence: float | None = None


@dataclass(frozen=True)
class ExtractedTable:
    """A table detected in the document, stored as a grid of text."""

    page_number: int
    rows: list[list[str]]


@dataclass(frozen=True)
class PageContent:
    """The text lines found on one page."""

    page_number: int
    lines: list[str]


@dataclass
class AnalysisResult:
    """Model-independent result. Each model fills only the parts it produces."""

    model: AnalysisModel
    fields: list[ExtractedField] = field(default_factory=list)
    line_items: list[dict[str, str]] = field(default_factory=list)
    key_value_pairs: list[KeyValuePair] = field(default_factory=list)
    tables: list[ExtractedTable] = field(default_factory=list)
    pages: list[PageContent] = field(default_factory=list)