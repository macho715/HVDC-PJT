# Email Knowledge Pipeline

## 1. Capture (Outlook VBA)
- Trigger `Application_NewMailEx` before Outlook rules.
- Mirror with `Items.ItemAdd` for post-rule moves.
- Save messages as `.msg` (Unicode) under a structured root per day.
- Store attachments with the same EntryID prefix.

## 2. Parse (Python `extract-msg`)
- Use `EmailParser` to decode `.msg` metadata, text, HTML, and attachments.
- Normalize recipients, headers, and categories for RFC 5322 compliance.
- Generate JSON-LD snapshots via `OntologyBuilder` (`schema.org/EmailMessage`).

## 3. Persist (Supabase + pgvector)
- Tables: `emails`, `email_attachments`, `email_ontology`, `email_embeddings`.
- Enforce RLS so only service roles can write, client apps read via PostgREST.
- Use `SupabaseEmailRepository` for structured upserts.

## 4. Embed & Search
- Default embedding model: `text-embedding-3-small` (OpenAI).
- `EmailIngestionService` chunks bodies (≤800 chars) before embedding.
- Store vectors in pgvector through the `vecs` client.
- Combine vector similarity with SQL filters for scoped retrieval.

## 5. Operations Checklist
- Weekly backfill job uses `NewMailEx` EntryIDs to detect gaps.
- Monitor capture rate ≥99.5%, embedding latency ≤0.30s/document.
- Block plaintext secrets; load keys with `.env` → `SupabaseSettings.from_env()`.

## 6. Local-First Option
- Swap Supabase for `sqlite-vec` during air-gapped pilots.
- Reuse the same parser and ontology layers.
- Replace embeddings with deterministic hashing for offline smoke tests.
