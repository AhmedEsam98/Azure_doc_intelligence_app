import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    endpoint: str
    key: str

    @classmethod
    def load(cls) -> "Settings":
        endpoint = os.getenv("AZURE_DI_ENDPOINT", "").strip()
        key = os.getenv("AZURE_DI_KEY", "").strip()

        if not endpoint or not key:
            raise ValueError(
                "Missing AZURE_DI_ENDPOINT or AZURE_DI_KEY. "
                "Set them in your .env file."
            )
        return cls(endpoint=endpoint, key=key)