"""이메일 파이프라인 단위 테스트 | Email pipeline unit tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, cast

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from email_pipeline import (
    EmailIngestionService,
    EmailParser,
    OntologyBuilder,
    SupabaseEmailRepository,
    SupabaseSettings,
)
from email_pipeline.models import EmbeddingPayload, OntologySnapshot
from email_pipeline.parser import MessageProtocol


class FakeAttachment:
    """테스트용 첨부 모형 | Test attachment mock."""

    def __init__(
        self, name: Optional[str], data: bytes, cid: Optional[str] = None
    ) -> None:
        """모형 첨부를 초기화 | Initialize attachment mock."""

        self.longFilename: Optional[str] = name
        self.shortFilename: Optional[str] = name
        self.data: bytes = data
        self._cid = cid
        self._mime = "text/plain"

    @property
    def cid(self) -> Optional[str]:
        """CID 반환 | Return CID."""

        return self._cid

    @property
    def mimeType(self) -> Optional[str]:
        """MIME 타입 반환 | Return MIME type."""

        return self._mime


class FakeMessage:
    """테스트용 메시지 모형 | Test message mock."""

    def __init__(self, attachments: Iterable[FakeAttachment]) -> None:
        """모형 메시지를 초기화 | Initialize message mock."""

        self.subject: str = "HVDC status report"
        self.sender: str = "planner@example.com"
        self.to: Optional[str] = "ops@example.com;manager@example.com"
        self.cc: Optional[str] = "lead@example.com"
        self.bcc: Optional[str] = ""
        self.date: str = "Fri, 12 Jul 2025 09:30:00 +0000"
        self.message_id: Optional[str] = "<sample@example.com>"
        self.header: str = (
            "Message-ID: <sample@example.com>\n"
            "In-Reply-To: <parent@example.com>\n"
            "References: <root@example.com> <parent@example.com>\n"
            "Thread-Topic: Logistics update"
        )
        self.body: str = "Body text for logistics update"
        self.htmlBody: Optional[str] = "<p>Body text for logistics update</p>"
        self.importance: Optional[str] = "Normal"
        self.categories: Optional[str] = "Logistics;HVDC"
        self.attachments: Sequence[FakeAttachment] = tuple(attachments)


class StubTable:
    """Supabase 테이블 모형 | Supabase table mock."""

    def __init__(self) -> None:
        """테이블 모형 초기화 | Initialize table mock."""

        self.rows: List[Any] = []

    def upsert(self, data: Any) -> Any:
        """업서트 호출 기록 | Record upsert call."""

        if isinstance(data, list):
            self.rows.extend(data)
        else:
            self.rows.append(data)
        return {"data": data}


class StubSupabaseClient:
    """Supabase 클라이언트 모형 | Supabase client mock."""

    def __init__(self) -> None:
        """클라이언트 모형 초기화 | Initialize client mock."""

        self.tables: Dict[str, StubTable] = {}

    def table(self, name: str) -> StubTable:
        """테이블 접근 제공 | Provide table access."""

        if name not in self.tables:
            self.tables[name] = StubTable()
        return self.tables[name]


class StubCollection:
    """Vecs 컬렉션 모형 | Vecs collection mock."""

    def __init__(self) -> None:
        """컬렉션 모형 초기화 | Initialize collection mock."""

        self.records: List[tuple[str, list[float], Dict[str, Any]]] = []

    def upsert(
        self, records: Iterable[tuple[str, list[float], Dict[str, Any]]]
    ) -> None:
        """업서트 호출 기록 | Record upsert call."""

        self.records.extend(records)


class StubEmbeddingProvider:
    """임베딩 제공자 모형 | Embedding provider mock."""

    def embed(self, text: str, metadata: Dict[str, str]) -> List[float]:
        """임베딩을 모사 | Simulate embedding."""

        base = float(len(text))
        return [round(base / 100, 2), round(base / 200, 2), round(base / 300, 2)]


def build_parser(tmp_path: Path) -> EmailParser:
    """테스트용 파서 생성 | Build parser for tests."""

    attachments = [FakeAttachment("report.txt", b"sample data")]
    message = FakeMessage(attachments)

    def loader(_: Path) -> MessageProtocol:
        return cast(MessageProtocol, message)

    return EmailParser(tmp_path, message_loader=loader)


def test_email_parser_extracts_metadata(tmp_path: Path) -> None:
    """파서가 메타데이터를 추출한다 | Parser extracts metadata."""

    parser = build_parser(tmp_path)
    record = parser.parse(tmp_path / "mail.msg")
    assert record.subject == "HVDC status report"
    assert record.from_address == "planner@example.com"
    assert record.to_addresses == ["ops@example.com", "manager@example.com"]
    assert record.cc_addresses == ["lead@example.com"]
    assert record.has_attachments is True
    assert record.attachments[0].filename == "report.txt"
    assert record.attachments[0].storage_path.exists()


def test_ontology_builder_generates_json_ld(tmp_path: Path) -> None:
    """온톨로지 빌더가 JSON-LD를 생성 | Ontology builder generates JSON-LD."""

    parser = build_parser(tmp_path)
    record = parser.parse(tmp_path / "mail.msg")
    builder = OntologyBuilder()
    snapshot = builder.build(record)
    assert snapshot["@type"] == "EmailMessage"
    assert snapshot["sender"]["email"] == "planner@example.com"
    assert snapshot["messageAttachment"][0]["name"] == "report.txt"


def test_repository_persists_entities(tmp_path: Path) -> None:
    """저장소가 데이터를 보존한다 | Repository persists data."""

    parser = build_parser(tmp_path)
    record = parser.parse(tmp_path / "mail.msg")
    settings = SupabaseSettings(
        url="https://example.supabase.co",
        service_role_key="service",
        anon_key="anon",
    )
    client = StubSupabaseClient()
    collection = StubCollection()
    repository = SupabaseEmailRepository(
        settings, client, embedding_collection=collection
    )
    repository.upsert_email(record)
    repository.upsert_attachments(record)
    repository.upsert_ontology(
        OntologySnapshot(
            message_id=record.message_id, snapshot=record.ontology_snapshot or {}
        )
    )
    payload = EmbeddingPayload(
        message_id=record.message_id,
        chunk_id="chunk-1",
        vector=[0.1, 0.2, 0.3],
        metadata={"type": "body"},
    )
    repository.upsert_embeddings([payload])
    assert client.tables[settings.emails_table].rows
    assert client.tables[settings.attachments_table].rows
    assert client.tables[settings.ontology_table].rows
    assert collection.records


def test_parser_deduplicates_duplicate_attachment_names(tmp_path: Path) -> None:
    """중복된 첨부 파일명이 덮어쓰기 되지 않는다 | Duplicate attachments keep unique names."""

    attachments = [
        FakeAttachment("image001.png", b"first"),
        FakeAttachment("image001.png", b"second"),
        FakeAttachment("image001.png", b"third"),
    ]
    message = FakeMessage(attachments)

    def loader(_: Path) -> MessageProtocol:
        return cast(MessageProtocol, message)

    parser = EmailParser(tmp_path, message_loader=loader)
    record = parser.parse(tmp_path / "mail.msg")

    filenames = [attachment.filename for attachment in record.attachments]
    assert filenames == ["image001.png", "image001_1.png", "image001_2.png"]

    stored_bytes = [attachment.storage_path.read_bytes() for attachment in record.attachments]
    assert stored_bytes == [b"first", b"second", b"third"]


def test_parser_deduplicates_after_sanitizing_names(tmp_path: Path) -> None:
    """Sanitized filenames still receive unique suffixes when duplicates arise."""

    attachments = [
        FakeAttachment("r eport?.pdf", b"first"),
        FakeAttachment("r!eport.pdf", b"second"),
    ]
    message = FakeMessage(attachments)

    parser = EmailParser(tmp_path, message_loader=lambda _: cast(MessageProtocol, message))
    record = parser.parse(tmp_path / "mail.msg")

    filenames = [attachment.filename for attachment in record.attachments]
    assert filenames == ["report.pdf", "report_1.pdf"]

    stored_bytes = [attachment.storage_path.read_bytes() for attachment in record.attachments]
    assert stored_bytes == [b"first", b"second"]


def test_parser_preserves_multi_suffix_extensions(tmp_path: Path) -> None:
    """Multi-extension files keep their suffix chain when deduplicated."""

    attachments = [
        FakeAttachment("archive.tar.gz", b"first"),
        FakeAttachment("archive.tar.gz", b"second"),
    ]
    message = FakeMessage(attachments)

    parser = EmailParser(tmp_path, message_loader=lambda _: cast(MessageProtocol, message))
    record = parser.parse(tmp_path / "mail.msg")

    filenames = [attachment.filename for attachment in record.attachments]
    assert filenames == ["archive.tar.gz", "archive_1.tar.gz"]

    stored_bytes = [attachment.storage_path.read_bytes() for attachment in record.attachments]
    assert stored_bytes == [b"first", b"second"]


def test_parser_handles_missing_attachment_names(tmp_path: Path) -> None:
    """Unnamed attachments are stored with generated unique filenames."""

    attachments = [
        FakeAttachment("", b"first"),
        FakeAttachment("???", b"second"),
        FakeAttachment(None, b"third"),
    ]
    message = FakeMessage(attachments)

    parser = EmailParser(tmp_path, message_loader=lambda _: cast(MessageProtocol, message))
    record = parser.parse(tmp_path / "mail.msg")

    filenames = [attachment.filename for attachment in record.attachments]
    assert len(filenames) == len(set(filenames))
    assert all(name.startswith("attachment") for name in filenames)

    stored_bytes = [attachment.storage_path.read_bytes() for attachment in record.attachments]
    assert stored_bytes == [b"first", b"second", b"third"]


def test_ingestion_service_runs_full_pipeline(tmp_path: Path) -> None:
    """수집 서비스가 전체 파이프라인 실행 | Ingestion service runs pipeline."""

    parser = build_parser(tmp_path)
    settings = SupabaseSettings(
        url="https://example.supabase.co",
        service_role_key="service",
        anon_key="anon",
    )
    client = StubSupabaseClient()
    collection = StubCollection()
    repository = SupabaseEmailRepository(
        settings, client, embedding_collection=collection
    )
    provider = StubEmbeddingProvider()
    service = EmailIngestionService(
        settings, repository, parser, embedding_provider=provider
    )
    record = service.ingest(tmp_path / "mail.msg", entry_id="ENTRY-1")
    assert record.entry_id == "ENTRY-1"
    assert client.tables[settings.emails_table].rows
    assert collection.records


def test_supabase_settings_from_env(monkeypatch: Any) -> None:
    """환경 변수에서 설정을 로드 | Load settings from environment."""

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-key")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-key")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    settings = SupabaseSettings.from_env()
    assert settings.url == "https://example.supabase.co"
    assert settings.service_role_key == "service-key"
    assert settings.anon_key == "anon-key"
    assert settings.openai_api_key == "sk-test"
