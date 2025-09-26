"""이메일 적재 파이프라인 테스트입니다. EN: Tests for the email ingestion pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, cast

import pytest

from src.models.email_entities import (
    HSCodeValidator,
    IncotermValidator,
    extract_hs_codes,
    extract_incoterm,
)
from src.services.email_ingestion import (
    AttachmentLike,
    EmailEmbeddingService,
    EmailIngestionPipeline,
    EmailMsgParser,
    ParsedEmail,
    SupabaseVectorStore,
)


class DummyAttachment:
    """테스트용 첨부입니다. EN: Dummy attachment used for testing."""

    def __init__(self, file_name: str, payload: bytes) -> None:
        self.longFilename: Optional[str] = file_name
        self.shortFilename: Optional[str] = file_name
        self.mimeType: Optional[str] = "application/octet-stream"
        self.cid: Optional[str] = "cid-001"
        self._payload = payload

    def save(self, customPath: str, customFilename: str | None = None) -> None:
        """첨부를 저장합니다. EN: Save attachment payload to disk."""

        file_name = customFilename or self.longFilename or "attachment.bin"
        target = Path(customPath) / file_name
        target.write_bytes(self._payload)


class DummyMessage:
    """테스트용 메시지입니다. EN: Dummy message used for testing."""

    def __init__(
        self, header: str, body: str, attachments: Sequence[AttachmentLike]
    ) -> None:
        self.subject: Optional[str] = "Transformer Delivery Update"
        self.sender: Optional[str] = "planner@hvdc.local"
        self.to: Optional[str] = "ops@hvdc.local"
        self.cc: Optional[str] = "qa@hvdc.local"
        self.bcc: Optional[str] = None
        self.date: Optional[str] = "Mon, 12 Aug 2024 10:00:00 +0000"
        self.header = header
        self.body = body
        self.htmlBody: Optional[str] = None
        self.attachments: Sequence[AttachmentLike] = attachments


class MemoryTable:
    """메모리 테이블 더미입니다. EN: In-memory table stub for upserts."""

    def __init__(self) -> None:
        self.rows: List[Dict[str, object]] = []

    def upsert(self, data: Mapping[str, object]) -> None:
        """업서트 호출을 기록합니다. EN: Store upsert payload for assertions."""

        self.rows.append(dict(data))


@pytest.fixture()
def sample_body() -> str:
    """샘플 본문을 제공합니다. EN: Provide sample email body."""

    return Path("tests/fixtures/sample_email_body.txt").read_text(encoding="utf-8")


def test_validators_load_resources() -> None:
    """리소스에서 인코텀과 HS 코드를 읽습니다. EN: Load Incoterm and HS code resources."""

    terms = IncotermValidator.load_terms()
    codes = HSCodeValidator.load_codes()
    assert "DDP" in terms
    assert "85043180" in codes


def test_extractors_from_body(sample_body: str) -> None:
    """본문에서 메타데이터를 추출합니다. EN: Extract metadata from body text."""

    assert extract_incoterm(sample_body) == "DDP"
    assert extract_hs_codes(sample_body) == ["85043180"]


def test_parser_builds_record(tmp_path: Path, sample_body: str) -> None:
    """파서가 이메일 레코드를 생성합니다. EN: Parser builds structured email record."""

    header = (
        "Message-ID: <1234@hvdc.local>\n"
        "In-Reply-To: <abcd@hvdc.local>\n"
        "References: <abcd@hvdc.local> <efgh@hvdc.local>\n"
    )
    attachment = DummyAttachment("invoice.pdf", b"binary-data")
    parser = EmailMsgParser(attachment_dir=tmp_path)
    parsed = parser.parse_message(
        DummyMessage(header=header, body=sample_body, attachments=[attachment]),
        source_path=tmp_path / "sample.msg",
    )
    record = parsed.record
    assert record.message_id == "<1234@hvdc.local>"
    assert record.incoterm == "DDP"
    assert record.hs_codes == ["85043180"]
    assert record.attachments[0].file_path.exists()
    json_ld = parsed.ontology
    identifier = cast(str, json_ld["identifier"])
    about_block = cast(Dict[str, object], json_ld["about"])
    term_code = cast(str, about_block["termCode"])
    assert identifier == "<1234@hvdc.local>"
    assert term_code == "DDP"


def test_pipeline_ingest_writes_to_store(tmp_path: Path, sample_body: str) -> None:
    """파이프라인이 벡터 스토어에 업서트합니다. EN: Pipeline writes parsed data to store."""

    header = "Message-ID: <z001@hvdc.local>\n"
    attachment = DummyAttachment("packing-list.pdf", b"payload")
    parser = EmailMsgParser(attachment_dir=tmp_path)
    parsed = parser.parse_message(
        DummyMessage(header=header, body=sample_body, attachments=[attachment]),
        source_path=tmp_path / "sample.msg",
    )

    email_table = MemoryTable()
    embedding_table = MemoryTable()

    def table_factory(name: str) -> MemoryTable:
        return email_table if name == "emails" else embedding_table

    embeddings: List[List[float]] = [[0.1, 0.2, 0.3]]

    def fake_embed(*, texts: Sequence[str], model: str) -> List[List[float]]:
        assert model == "text-embedding-3-small"
        assert texts
        return embeddings

    pipeline = EmailIngestionPipeline(
        parser=parser,
        embedding_service=EmailEmbeddingService(fake_embed),
        vector_store=SupabaseVectorStore(table_factory, table_factory),
        chunk_size=50,
    )

    class StubParser(EmailMsgParser):
        def __init__(self, parsed_email: ParsedEmail) -> None:
            self._parsed_email = parsed_email

        def parse_path(self, msg_path: Path) -> ParsedEmail:
            return self._parsed_email

    pipeline.parser = StubParser(parsed)
    result = pipeline.ingest(tmp_path / "sample.msg")
    assert result.record.message_id == "<z001@hvdc.local>"
    assert email_table.rows
    stored_embedding_raw = cast(str, embedding_table.rows[0]["embedding"])
    stored_embedding = json.loads(stored_embedding_raw)
    assert stored_embedding == [0.1, 0.2, 0.3]
