"""물류 도메인 공통 Pydantic 베이스 | Shared Pydantic base for logistics domain."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class LogiBaseModel(BaseModel):
    """로지스틱스 기본 모델 정의 | Define base logistics model."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
