# 이메일 지식 파이프라인

## 1. 수집 (Outlook VBA)
- 규칙 적용 전 `Application_NewMailEx` 이벤트로 선수집.
- 규칙 이후 이동을 대비해 `Items.ItemAdd`를 병행.
- 메시지는 `.msg`(Unicode)로 일자별 폴더에 저장.
- 첨부 파일은 EntryID 접두어로 동일 폴더에 저장.

## 2. 파싱 (Python `extract-msg`)
- `EmailParser`로 메타데이터·본문·HTML·첨부를 표준화.
- 수신자, 헤더, 카테고리를 RFC 5322 기준으로 정규화.
- `OntologyBuilder`로 `schema.org/EmailMessage` JSON-LD 생성.

## 3. 저장 (Supabase + pgvector)
- 테이블: `emails`, `email_attachments`, `email_ontology`, `email_embeddings`.
- RLS로 서비스 롤만 쓰기 허용, 클라이언트는 PostgREST 읽기.
- `SupabaseEmailRepository`를 통해 구조화 업서트 처리.

## 4. 임베딩·검색
- 기본 임베딩 모델: `text-embedding-3-small` (OpenAI).
- `EmailIngestionService`가 본문을 800자 이하로 청크 분리.
- 벡터는 `vecs` 클라이언트를 통해 pgvector에 저장.
- 벡터 유사도 + SQL 필터 결합으로 정밀 검색.

## 5. 운영 체크리스트
- 주간 백필 작업으로 `NewMailEx` EntryID 누락 감시.
- 캡처율 ≥99.5%, 임베딩 지연 ≤0.30초/문서 모니터링.
- 평문 비밀 금지, `.env` → `SupabaseSettings.from_env()`로 키 로드.

## 6. 로컬-우선 옵션
- 격리 환경에서는 Supabase 대신 `sqlite-vec`로 대체.
- 파서·온톨로지 레이어는 동일하게 재사용.
- 오프라인 검증은 결정적 해시 기반 임베딩으로 대체 가능.
