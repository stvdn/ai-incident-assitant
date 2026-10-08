from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy import String, Text, DateTime, func, Integer, CheckConstraint

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
