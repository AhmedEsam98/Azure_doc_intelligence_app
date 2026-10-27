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

## Project structure

```
app.py                      Composition root (wires everything together)
Dockerfile                  Container image definition
.dockerignore               Files excluded from the image

.env.example                Template for the required environment variables
requirements.txt            Python dependencies
src/
├── config/                 Settings loaded from .env
├── domain/                 Entities and the DocumentAnalyzer interface (no dependencies)
├── application/            Use case and per-model mappers (pandas only)
├── infrastructure/         Azure adapter (the only code that knows Azure)
└── presentation/           Streamlit components and table rendering
```

Dependencies point inward: presentation → application → domain, and infrastructure implements the domain interface.

## Configuration

Create a `.env` file in the project root (see `.env.example`):

```
AZURE_DI_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
AZURE_DI_KEY=<your-key>
```

Get both values from the Azure Portal under your Document Intelligence resource → **Keys and Endpoint**.

Do not wrap the values in quotes or put spaces around `=` (this matters for Docker's `--env-file`).

## Run locally

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows

source .venv/bin/activate     # macOS / Linux
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

## Run with Docker

Build the image:

```bash
docker build -t doc-intelligence-app .
```

Run it, passing your Azure credentials from `.env`:

```bash
docker run --rm -p 8501:8501 --env-file .env doc-intelligence-app
```

Then open http://localhost:8501. The `.env` file is never copied into the image; credentials are supplied at run time.

## Notes


- Uses `azure-ai-formrecognizer==3.3.3`, which still supports all five models including General Document (`prebuilt-document`).
- The free tier (F0) analyzes only the first 2 pages and accepts files up to 4 MB.
- The preview shows the first 5 pages of a PDF; analysis covers the whole document.

## Common errors

| Symptom | Fix |
|---|---|
| Missing `AZURE_DI_ENDPOINT` or `AZURE_DI_KEY` | Check `.env` and run from the project root |
| Access denied / invalid key | Re-copy the key and endpoint from the Azure Portal. With Docker, remove quotes from `.env` values |
| Resource not found | Verify the endpoint and the model's regional availability |
| Too many requests (429) | Wait a few seconds and try again |
| App not reachable in Docker | Open http://localhost:8501, not the `0.0.0.0` address shown in the logs |

## Tech stack

Python, Streamlit, Azure AI Document Intelligence, pandas, PyMuPDF, Pillow, Docker