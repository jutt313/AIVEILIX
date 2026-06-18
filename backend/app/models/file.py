import uuid
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    r2_path: Mapped[str] = mapped_column(Text, nullable=False)
    layout_json_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("uploading", "processing", "ready", "failed", name="file_status"),
        nullable=False,
        default="uploading",
        index=True,
    )
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    image_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    section_outline: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_agent_written: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bucket: Mapped["Bucket"] = relationship("Bucket", back_populates="files")
    category: Mapped["Category | None"] = relationship("Category", back_populates="files")
    versions: Mapped[list["FileVersion"]] = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan")
    chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="file", cascade="all, delete-orphan")
    summaries: Mapped[list["Summary"]] = relationship("Summary", back_populates="file", cascade="all, delete-orphan")
    investigation_events: Mapped[list["InvestigationEvent"]] = relationship("InvestigationEvent", back_populates="file", cascade="all, delete-orphan")
    error_logs: Mapped[list["ErrorLog"]] = relationship("ErrorLog", back_populates="file")


class FileVersion(Base):
    __tablename__ = "file_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    r2_path: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    file: Mapped["File"] = relationship("File", back_populates="versions")
