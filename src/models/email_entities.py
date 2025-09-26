"""이메일 지식베이스 엔터티 모델입니다. EN: Email knowledge base entity models."""

from __future__ import annotations

import csv
import re
from datetime import datetime
from email.parser import HeaderParser
from pathlib import Path
from typing import ClassVar, Dict, Iterable, List, Optional, Set

import yaml  # type: ignore[import-untyped]
from pydantic import Field

from .logi_base import Currency, LogiBaseModel

RESOURCE_ROOT = Path(__file__).resolve().parents[2] / "resources"


class IncotermValidator:
    """인코텀 유효성을 검증합니다. EN: Validate Incoterm values."""

    _cache: ClassVar[Set[str]] = set()

    @classmethod
    def load_terms(cls) -> Set[str]:
        """인코텀 목록을 불러옵니다. EN: Load allowed Incoterm codes."""

        if cls._cache:
            return cls._cache
        incoterm_file = RESOURCE_ROOT / "incoterm.yaml"
        if not incoterm_file.exists():
            raise FileNotFoundError(f"Incoterm resource missing: {incoterm_file}")
        data = yaml.safe_load(incoterm_file.read_text(encoding="utf-8"))
        terms = data.get("incoterms_2020", [])
        cls._cache = {term.upper() for term in terms}
        return cls._cache

    @classmethod
    def validate(cls, value: Optional[str]) -> Optional[str]:
        """인코텀 값을 검증합니다. EN: Validate and normalize an Incoterm value."""

        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized:
            return None
        allowed = cls.load_terms()
        if normalized not in allowed:
            raise ValueError(f"Unsupported Incoterm: {normalized}")
        return normalized


class HSCodeValidator:
    """HS 코드 유효성을 검증합니다. EN: Validate HS code values."""

    _cache: ClassVar[Set[str]] = set()

    @classmethod
    def load_codes(cls) -> Set[str]:
        """HS 코드 목록을 불러옵니다. EN: Load allowed HS codes."""

        if cls._cache:
            return cls._cache
        hs_file = RESOURCE_ROOT / "hs2022.csv"
        if not hs_file.exists():
            raise FileNotFoundError(f"HS code resource missing: {hs_file}")
        with hs_file.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            cls._cache = {
                row["hs_code"].strip() for row in reader if row.get("hs_code")
            }
        return cls._cache

    @classmethod
    def validate_many(cls, values: Iterable[str]) -> List[str]:
        """HS 코드 목록을 검증합니다. EN: Validate multiple HS codes."""

        allowed = cls.load_codes()
        validated: List[str] = []
        for value in values:
            normalized = value.strip()
            if not normalized:
                continue
            if normalized not in allowed:
                raise ValueError(f"Unsupported HS code: {normalized}")
            validated.append(normalized)
        return validated


class EmailAttachment(LogiBaseModel):
    """이메일 첨부 정보를 보관합니다. EN: Store metadata for an email attachment."""

    file_name: str
    file_path: Path
    content_type: Optional[str] = None
    content_id: Optional[str] = None
    size_bytes: int = 0


class EmailMessageRecord(LogiBaseModel):
    """지식베이스용 이메일 레코드입니다. EN: Email record ready for knowledge base."""

    message_id: str
    subject: str
    from_address: str
    to_addresses: List[str]
    cc_addresses: List[str]
    bcc_addresses: List[str]
    date_received: datetime
    incoterm: Optional[str] = None
    hs_codes: List[str] = Field(default_factory=list)
    body_text: str
    body_html: Optional[str] = None
    thread_references: List[str]
    headers: Dict[str, str]
    attachments: List[EmailAttachment]
    currency: Currency = Currency.AED

    @classmethod
    def from_raw(
        cls,
        *,
        message_id: str,
        subject: str,
        from_address: str,
        to_addresses: Iterable[str],
        cc_addresses: Iterable[str],
        bcc_addresses: Iterable[str],
        date_received: datetime,
        body_text: str,
        body_html: Optional[str],
        thread_references: Iterable[str],
        headers: Dict[str, str],
        attachments: Iterable[EmailAttachment],
        incoterm: Optional[str] = None,
        hs_codes: Optional[Iterable[str]] = None,
        currency: Currency = Currency.AED,
    ) -> "EmailMessageRecord":
        """원시 데이터를 이메일 레코드로 변환합니다. EN: Build record from raw components."""

        normalized_incoterm = IncotermValidator.validate(incoterm)
        validated_hs_codes = HSCodeValidator.validate_many(hs_codes or [])
        return cls(
            message_id=message_id,
            subject=subject.strip(),
            from_address=from_address.strip(),
            to_addresses=sorted(
                {addr.strip() for addr in to_addresses if addr.strip()}
            ),
            cc_addresses=sorted(
                {addr.strip() for addr in cc_addresses if addr.strip()}
            ),
            bcc_addresses=sorted(
                {addr.strip() for addr in bcc_addresses if addr.strip()}
            ),
            date_received=date_received,
            incoterm=normalized_incoterm,
            hs_codes=validated_hs_codes,
            body_text=body_text.strip(),
            body_html=body_html.strip() if body_html else None,
            thread_references=[ref.strip() for ref in thread_references if ref.strip()],
            headers={key: value.strip() for key, value in headers.items()},
            attachments=list(attachments),
            currency=currency,
        )

    def to_json_ld(self) -> Dict[str, object]:
        """이메일을 JSON-LD로 변환합니다. EN: Convert email record into JSON-LD."""

        recipients = [
            {"@type": "ContactPoint", "email": address}
            for address in self.to_addresses + self.cc_addresses + self.bcc_addresses
        ]
        attachment_entries = [
            {
                "@type": "DigitalDocument",
                "name": item.file_name,
                "identifier": str(item.file_path),
                "encodingFormat": item.content_type,
                "contentSize": round(item.size_bytes, 2),
            }
            for item in self.attachments
        ]
        additional_props = [
            {"@type": "PropertyValue", "name": key, "value": value}
            for key, value in self.headers.items()
            if key.lower() in {"message-id", "in-reply-to", "references"}
        ]
        payload: Dict[str, object] = {
            "@context": "https://schema.org",
            "@type": "EmailMessage",
            "@id": f"urn:email:{self.message_id}",
            "identifier": self.message_id,
            "headline": self.subject,
            "dateReceived": self.date_received.isoformat(),
            "sender": {"@type": "ContactPoint", "email": self.from_address},
            "recipient": recipients,
            "mentions": [
                {
                    "@type": "DefinedTerm",
                    "name": "HSCode",
                    "termCode": code,
                }
                for code in self.hs_codes
            ],
            "text": self.body_text,
            "messageAttachment": attachment_entries,
            "additionalProperty": additional_props,
            "isPartOf": {
                "@type": "CreativeWork",
                "identifier": "HVDC-Supabase-KB",
            },
        }
        if self.incoterm:
            payload["about"] = {
                "@type": "DefinedTerm",
                "name": "Incoterm",
                "termCode": self.incoterm,
            }
        return payload

    @staticmethod
    def parse_headers(raw_header: str) -> Dict[str, str]:
        """RFC5322 헤더를 파싱합니다. EN: Parse RFC 5322 headers into a dictionary."""

        parser = HeaderParser()
        message = parser.parsestr(raw_header)
        return {key: value for key, value in message.items()}


INCOTERM_PATTERN = re.compile(
    r"incoterm[s]?\s*[:\-]\s*(?P<code>[A-Z]{3})", re.IGNORECASE
)
HS_CODE_PATTERN = re.compile(r"hs\s*code\s*[:\-]?\s*(?P<code>\d{4,10})", re.IGNORECASE)


def extract_incoterm(text: str) -> Optional[str]:
    """본문에서 인코텀을 추출합니다. EN: Extract an Incoterm code from text."""

    match = INCOTERM_PATTERN.search(text)
    if not match:
        return None
    return match.group("code").upper()


def extract_hs_codes(text: str) -> List[str]:
    """본문에서 HS 코드를 추출합니다. EN: Extract HS codes from text."""

    codes = {match.group("code") for match in HS_CODE_PATTERN.finditer(text)}
    return sorted(codes)
