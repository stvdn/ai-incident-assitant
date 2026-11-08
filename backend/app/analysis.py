from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


AnalysisText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=4000,
    ),
]


class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    probable_cause: AnalysisText
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    evidence: list[AnalysisText] = Field(min_length=1, max_length=10)
    suggested_actions: list[AnalysisText] = Field(
        min_length=1,
        max_length=10,
    )


class AnalysisResponse(AnalysisResult):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    incident_id: UUID
    status: Literal["completed"]
    model: str
    latency_ms: int = Field(ge=0)
    created_at: datetime