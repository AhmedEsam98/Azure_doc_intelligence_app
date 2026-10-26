# Azure AI Document Intelligence with Streamlit

A Streamlit app that extracts information from documents using Azure AI Document Intelligence and shows the results in structured tables, side by side with the document preview.

**Flow:** Select Model → Upload Document → Analyze → View Structured Results

## Features

- Dropdown with 5 prebuilt models: Invoice, Receipt, Read, Layout, General Document
- Upload PDF or image files (PNG, JPG, BMP, TIFF) with a live preview
- Results shown next to the document for easy comparison
- Result tables adapted to each model
- CSV download for every table
- Clean architecture: swapping Azure for another analyzer means writing one new class
- Docker support

## What each model returns

| Model | Tables shown |
|---|---|
| Prebuilt Invoice | Extracted Fields, Line Items |
| Prebuilt Receipt | Extracted Fields, Line Items |
| Prebuilt Read | Text Lines |
| Prebuilt Layout | Detected Tables, Text Lines |
| Prebuilt General Document | Key-Value Pairs, Detected Tables, Text Lines |

## Architecture

```
app.py                      Composition root (wires everything together)
src/
├── config/                 Settings loaded from .env

├── domain/                 Entities and the DocumentAnalyzer interface (no dependencies)
├── application/            Use case and per-model mappers (pandas only)
├── infrastructure/         Azure adapter (the only code that knows Azure)
└── presentation/           Streamlit components and table rendering
```

Dependencies point inward: presentation → application → domain, and infrastructure implements the domain interface.

## Configuration

Create a `.env` file in the project root (see `.env.example`). Write the values without quotes:

```
AZURE_DI_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
AZURE_DI_KEY=<your-key>
```

Get both values from the Azure Portal under your Document Intelligence resource → **Keys and Endpoint**.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.


## Run with Docker

Requires Docker Desktop. The `.env` file is passed at runtime and is never copied into the image.

With Docker Compose:

```bash
docker compose up --build
```

Without Compose:

```bash
docker build -t doc-intelligence-app .
docker run --rm -p 8501:8501 --env-file .env doc-intelligence-app
```

Open http://localhost:8501. Stop with `Ctrl+C` (and `docker compose down` if you used Compose).

## Notes

- Uses `azure-ai-formrecognizer==3.3.3`, which still supports all five models including General Document (`prebuilt-document`).
- The free tier (F0) analyzes only the first 2 pages and accepts files up to 4 MB.
- The preview shows the first 5 pages of a PDF; analysis covers the whole document.

## Common errors

| Symptom | Fix |
|---|---|
| Missing `AZURE_DI_ENDPOINT` or `AZURE_DI_KEY` | Check `.env` (no quotes) and run from the project root |
| Access denied / invalid key | Re-copy the key and endpoint from the Azure Portal |
| Resource not found | Verify the endpoint and the model's regional availability |

| Too many requests (429) | Wait a few seconds and try again |
| Port 8501 already allocated | Stop the other Streamlit process or container |

## Tech stack

Python, Streamlit, Azure AI Document Intelligence, pandas, PyMuPDF, Pillow, Docker