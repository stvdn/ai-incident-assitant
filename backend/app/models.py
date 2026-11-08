from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy import String, Text, DateTime, func, Integer, CheckConstraint, Float, ForeignKey


class Base(DeclarativeBase):
    pass

class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        CheckConstraint(
            "octet_length(log) <= 65536",
            name="ck_incidents_log_max_bytes"
        ),
        CheckConstraint(
            "log ~ '[^[:space:]]'",
            name="ck_incidents_log_not_blank",
        ),
        CheckConstraint(
            "job_name ~ '[^[:space:]]'",
            name="ck_incidents_job_name_not_blank",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    job_name: Mapped[str] = mapped_column(String(200), nullable=False)
    log: Mapped[str] = mapped_column(Text, nullable=False)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

class IncidentAnalysis(Base):
    __tablename__ = "incident_analyses"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_incident_analyses_confidence",
        ),
        CheckConstraint(
            "latency_ms >= 0",
            name="ck_incident_analyses_latency",
        ),
        CheckConstraint(
            "status = 'completed'",
            name="ck_incident_analyses_status",
        ),
        CheckConstraint(
            "probable_cause ~ '[^[:space:]]'",
            name="ck_incident_analyses_cause_not_blank",
        ),
        CheckConstraint(
            "model ~ '[^[:space:]]'",
            name="ck_incident_analyses_model_not_blank",
        ),
        CheckConstraint(
            "jsonb_typeof(evidence) = 'array' "
            "AND jsonb_array_length(evidence) BETWEEN 1 AND 10",
            name="ck_incident_analyses_evidence",
        ),
        CheckConstraint(
            "jsonb_typeof(suggested_actions) = 'array' "
            "AND jsonb_array_length(suggested_actions) BETWEEN 1 AND 10",
            name="ck_incident_analyses_actions",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    incident_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )
    probable_cause: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    suggested_actions: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="completed",
    )
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

