"""Outlook 이메일 지식베이스 파이프라인입니다. EN: Outlook email knowledge base pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Protocol, Sequence

from src.models.email_entities import (
    EmailAttachment,
    EmailMessageRecord,
    extract_hs_codes,
    extract_incoterm,
)

try:
    import extract_msg
except ImportError:  # pragma: no cover
    extract_msg = None


class AttachmentLike(Protocol):
    """Outlook 첨부 인터페이스입니다. EN: Protocol describing Outlook attachment API."""

    longFilename: Optional[str]
    shortFilename: Optional[str]
    mimeType: Optional[str]
    cid: Optional[str]

    def save(
        self, customPath: str, customFilename: Optional[str] | None = None
    ) -> None:
        """첨부 파일을 저장합니다. EN: Save attachment to provided directory."""


class MessageLike(Protocol):
    """Outlook 메시지 인터페이스입니다. EN: Protocol describing Outlook message API."""

    subject: Optional[str]
    sender: Optional[str]
    to: Optional[str]
    cc: Optional[str]
    bcc: Optional[str]
    date: Optional[str]
    header: str
    body: str
    htmlBody: Optional[str]
    attachments: Sequence[AttachmentLike]


@dataclass(slots=True)
class ParsedEmail:
    """파싱된 이메일 데이터를 보관합니다. EN: Container for parsed email data."""

    record: EmailMessageRecord
    ontology: Dict[str, object]


class EmailMsgParser:
    """`.msg` 파일을 파싱합니다. EN: Parse `.msg` files into structured records."""

    def __init__(self, attachment_dir: Path) -> None:
        self.attachment_dir = attachment_dir
        self.attachment_dir.mkdir(parents=True, exist_ok=True)

    def parse_path(self, msg_path: Path) -> ParsedEmail:
        """경로에서 메시지를 읽습니다. EN: Parse Outlook message from path."""

        if extract_msg is None:  # pragma: no cover
            raise RuntimeError("extract-msg package is not available")
        message = extract_msg.Message(str(msg_path))
        return self.parse_message(message, source_path=msg_path)

    def parse_message(self, message: MessageLike, *, source_path: Path) -> ParsedEmail:
        """메시지 객체를 파싱합니다. EN: Parse message-like object into record."""

        headers = EmailMessageRecord.parse_headers(message.header)
        message_id = headers.get("Message-ID") or f"local-{source_path.stem}"
        date_value = self._parse_date(message.date)
        to_addresses = self._split_addresses(message.to)
        cc_addresses = self._split_addresses(message.cc)
        bcc_addresses = self._split_addresses(message.bcc)
        incoterm_candidate = extract_incoterm(message.body)
        hs_candidates = extract_hs_codes(message.body)
        attachments = self._persist_attachments(message.attachments)
        record = EmailMessageRecord.from_raw(
            message_id=message_id,
            subject=message.subject or "(no subject)",
            from_address=message.sender
            or "unknown@local",  # fallback avoids empty strings
            to_addresses=to_addresses,
            cc_addresses=cc_addresses,
            bcc_addresses=bcc_addresses,
            date_received=date_value,
            body_text=message.body,
            body_html=message.htmlBody,
            thread_references=self._thread_references(headers),
            headers=headers,
            attachments=attachments,
            incoterm=incoterm_candidate,
            hs_codes=hs_candidates,
        )
        ontology = record.to_json_ld()
        return ParsedEmail(record=record, ontology=ontology)

    def _persist_attachments(
        self, attachments: Sequence[AttachmentLike]
    ) -> List[EmailAttachment]:
        """첨부 파일을 저장합니다. EN: Save attachments and return metadata."""

        saved: List[EmailAttachment] = []
        for item in attachments:
            file_name = item.longFilename or item.shortFilename or "attachment.bin"
            target_path = self.attachment_dir / file_name
            item.save(customPath=str(self.attachment_dir), customFilename=file_name)
            size_bytes = target_path.stat().st_size if target_path.exists() else 0
            saved.append(
                EmailAttachment(
                    file_name=file_name,
                    file_path=target_path,
                    content_type=item.mimeType,
                    content_id=item.cid,
                    size_bytes=size_bytes,
                )
            )
        return saved

    @staticmethod
    def _split_addresses(raw: Optional[str]) -> List[str]:
        """주소 문자열을 분리합니다. EN: Split raw address string into list."""

        if not raw:
            return []
        candidates = [segment.strip() for segment in raw.replace(";", ",").split(",")]
        return [candidate for candidate in candidates if candidate]

    @staticmethod
    def _parse_date(raw_date: Optional[str]) -> datetime:
        """문자열 날짜를 파싱합니다. EN: Convert raw string date into datetime."""

        if raw_date:
            try:
                parsed = parsedate_to_datetime(raw_date)
                if parsed is not None:
                    return parsed
            except (TypeError, ValueError):
                pass
        return datetime.utcnow()

    @staticmethod
    def _thread_references(headers: Dict[str, str]) -> List[str]:
        """스레드 참조를 수집합니다. EN: Collect threading references from headers."""

        references: List[str] = []
        in_reply = headers.get("In-Reply-To")
        if in_reply:
            references.append(in_reply)
        for value in headers.get("References", "").split():
            cleaned = value.strip()
            if cleaned:
                references.append(cleaned)
        return references


class EmbeddingFunction(Protocol):
    """임베딩 함수 인터페이스입니다. EN: Protocol describing embedding callable."""

    def __call__(self, *, texts: Sequence[str], model: str) -> List[List[float]]:
        """텍스트 임베딩을 계산합니다. EN: Compute embeddings for text chunks."""


class EmailEmbeddingService:
    """OpenAI 임베딩을 관리합니다. EN: Manage embedding calls to OpenAI-like clients."""

    def __init__(
        self,
        embedding_callable: EmbeddingFunction,
        *,
        model: str = "text-embedding-3-small",
    ) -> None:
        self._callable = embedding_callable
        self.model = model

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        """텍스트에 대한 임베딩을 생성합니다. EN: Generate embeddings for provided texts."""

        if not texts:
            return []
        embeddings = self._callable(texts=texts, model=self.model)
        return [self._round_vector(vector) for vector in embeddings]

    @staticmethod
    def _round_vector(vector: Sequence[float]) -> List[float]:
        """벡터 값을 2자리로 반올림합니다. EN: Round vector values to two decimals."""

        return [round(value, 2) for value in vector]


from typing import Mapping


class VectorTableClient(Protocol):
    """Supabase 테이블 인터페이스입니다. EN: Protocol for Supabase table client."""

    def upsert(self, data: Mapping[str, object]) -> None:
        """행을 업서트합니다. EN: Upsert a single row."""


class SupabaseVectorStore:
    """Supabase 벡터 저장소 래퍼입니다. EN: Wrapper around Supabase vector store."""

    def __init__(
        self,
        email_table: Callable[[str], VectorTableClient],
        embedding_table: Callable[[str], VectorTableClient],
        *,
        email_table_name: str = "emails",
        embedding_table_name: str = "email_embeddings",
    ) -> None:
        self._email_table_factory = email_table
        self._embedding_table_factory = embedding_table
        self.email_table_name = email_table_name
        self.embedding_table_name = embedding_table_name

    def upsert_email(
        self, parsed: ParsedEmail, embeddings: Sequence[List[float]]
    ) -> None:
        """이메일과 임베딩을 Supabase에 저장합니다. EN: Upsert email and embeddings to Supabase."""

        record = parsed.record
        email_payload = {
            "message_id": record.message_id,
            "subject": record.subject,
            "from_address": record.from_address,
            "to_addresses": json.dumps(record.to_addresses, ensure_ascii=False),
            "cc_addresses": json.dumps(record.cc_addresses, ensure_ascii=False),
            "bcc_addresses": json.dumps(record.bcc_addresses, ensure_ascii=False),
            "date_received": record.date_received.isoformat(),
            "incoterm": record.incoterm,
            "hs_codes": json.dumps(record.hs_codes, ensure_ascii=False),
            "body_text": record.body_text,
            "body_html": record.body_html,
            "thread_references": json.dumps(
                record.thread_references, ensure_ascii=False
            ),
            "headers": json.dumps(record.headers, ensure_ascii=False),
            "ontology": json.dumps(parsed.ontology, ensure_ascii=False),
            "currency": str(record.currency),
        }
        self._email_table_factory(self.email_table_name).upsert(email_payload)
        for index, vector in enumerate(embeddings):
            embedding_payload = {
                "message_id": record.message_id,
                "chunk_id": index,
                "embedding": json.dumps(vector),
                "dimension": len(vector),
            }
            self._embedding_table_factory(self.embedding_table_name).upsert(
                embedding_payload
            )


class EmailIngestionPipeline:
    """이메일 → 벡터 파이프라인입니다. EN: Pipeline from email files to vector store."""

    def __init__(
        self,
        parser: EmailMsgParser,
        embedding_service: EmailEmbeddingService,
        vector_store: SupabaseVectorStore,
        *,
        chunk_size: int = 2048,
    ) -> None:
        self.parser = parser
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.chunk_size = chunk_size

    def ingest(self, msg_path: Path) -> ParsedEmail:
        """이메일을 적재합니다. EN: Ingest email file into knowledge base."""

        parsed = self.parser.parse_path(msg_path)
        text_chunks = self._chunk_text(parsed.record.body_text)
        embeddings = self.embedding_service.embed(text_chunks)
        self.vector_store.upsert_email(parsed, embeddings)
        return parsed

    def _chunk_text(self, text: str) -> List[str]:
        """본문을 청크로 분할합니다. EN: Split text body into embedding chunks."""

        clean_text = text.strip()
        if not clean_text:
            return []
        return [
            clean_text[index : index + self.chunk_size]
            for index in range(0, len(clean_text), self.chunk_size)
        ]
