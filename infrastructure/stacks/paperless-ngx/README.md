# Paperless-ngx — Document Management

OCR-backed document ingestion at `https://paperless.cianfhoghlaim.ie`. Login via PocketID SSO.

Upload PDFs, images, Office docs → auto-OCR + categorised by n8n LLM pipeline.
Summaries flow into Vikunja tasks. Federated with the OCR stack (Docling-Serve, OlmOCR).

Backed by PlanetScale "bunchloch" (schema: `paperless`).
