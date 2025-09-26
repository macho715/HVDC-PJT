"""물류 공통 Pydantic 기반 모델 정의입니다. EN: Shared Pydantic base models for logistics domain."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class LogiBaseModel(BaseModel):
    """물류 전용 기본 모델입니다. EN: Base model enforcing logistics data conventions."""

    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, validate_assignment=True
    )


class Currency(str, Enum):
    """통화 코드 열거형입니다. EN: Currency enumeration for monetary fields."""

    AED = "AED"
    USD = "USD"
    EUR = "EUR"
    SAR = "SAR"
    GBP = "GBP"

    def __str__(self) -> str:
        """통화 코드를 문자열로 반환합니다. EN: Return currency code as string."""

        return self.value
