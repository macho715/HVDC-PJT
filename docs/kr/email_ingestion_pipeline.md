# Outlook 이메일 지식베이스 파이프라인 요약 (KR)

## 개요
- Outlook VBA `NewMailEx` + `ItemAdd` 이벤트로 `.msg(Unicode)` 저장
- Python `extract-msg`로 메타데이터/본문/첨부 파싱
- Incoterm·HS 코드 리소스(`resources/incoterm.yaml`, `hs2022.csv`) 기반 검증
- schema.org `EmailMessage` JSON-LD 스냅샷 생성 및 Supabase(pgvector) 업서트 준비

## 핵심 구성
1. **`EmailMsgParser`**: `.msg` 파싱 및 첨부 저장
2. **`EmailMessageRecord`**: `LogiBaseModel` 기반 레코드 + 자동 검증
3. **`EmailEmbeddingService`**: OpenAI `text-embedding-3-small` 호출 추상화
4. **`SupabaseVectorStore`**: 이메일/벡터 테이블 업서트 래퍼
5. **`EmailIngestionPipeline`**: 파서→임베딩→Supabase 전체 오케스트레이션

## 테스트
- `tests/test_email_ingestion_pipeline.py`: 파서/검증/업서트 전 과정 TDD 보장
