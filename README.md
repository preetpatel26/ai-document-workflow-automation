# AI Document Workflow Automation

A portfolio demo that extracts structured shipment data from document text using an LLM, validates it, routes uncertain records for human review, and optionally forwards approved records to a REST API.

## Features
- FastAPI endpoints for processing and health checks
- OpenAI structured extraction with Pydantic validation
- Confidence-based human-review routing
- Optional downstream REST API integration with timeout and bounded retries
- Unit tests that run without a real API key or network access

## Quick start
Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Add OPENAI_API_KEY to .env for live extraction
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Example
```bash
curl -X POST http://127.0.0.1:8000/process -H "Content-Type: application/json" -d '{
  "document_text": "Shipment reference SHP-2048. Supplier: Northwind Parts. Pickup: Chicago, IL. Delivery: Dallas, TX. Pickup date: 2026-11-02. Three pallets.",
  "send_to_downstream": false
}'
```

If `OPENAI_API_KEY` is missing, live processing returns a clear configuration error. Unit tests use mocked extractors and do not require credentials.

## Endpoints
- `GET /health`
- `POST /process`
- `GET /review-queue` (in-memory demo queue only)

## Environment
See `.env.example`. Never commit `.env`, API keys, customer documents, or production data.

## Reliability notes
LLM output is treated as untrusted and validated before use. Low-confidence records are routed for human review. Downstream retries are bounded. In production, add durable storage, authentication, authorization, audit logs, monitoring, and an idempotency strategy before retrying non-idempotent operations.

## Portfolio description
Built a Python service that extracts structured shipment data from unstructured documents using an LLM, validates the result, routes incomplete or low-confidence records for human review, and optionally forwards approved records to a REST API. Includes error handling, configurable timeouts and retries, and unit tests with mocked dependencies.

Identify this as a personal demo, not client work. Only claim functionality you have tested.
