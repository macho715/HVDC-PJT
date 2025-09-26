# Outlook Email Knowledge Base Pipeline Summary (EN)

## Overview
- Capture `.msg` files via Outlook VBA `NewMailEx` + `ItemAdd` events
- Parse metadata, bodies, and attachments with Python `extract-msg`
- Validate Incoterms and HS codes using `resources/incoterm.yaml` and `hs2022.csv`
- Produce schema.org `EmailMessage` JSON-LD snapshots ready for Supabase (pgvector) storage

## Key Components
1. **`EmailMsgParser`**: Parses `.msg` files and persists attachments
2. **`EmailMessageRecord`**: `LogiBaseModel` entity with automatic validations
3. **`EmailEmbeddingService`**: Wraps OpenAI `text-embedding-3-small`
4. **`SupabaseVectorStore`**: Abstraction for email and embedding upserts
5. **`EmailIngestionPipeline`**: Orchestrates parsing → embedding → Supabase writes

## Testing
- `tests/test_email_ingestion_pipeline.py`: TDD coverage for parsing, validation, and upsert flow
