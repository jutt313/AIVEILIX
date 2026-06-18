import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False, index=True)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    block_id: Mapped[str] = mapped_column(String(255), nullable=False)
    nearby_image_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        Enum("pending", "embedded", "failed", name="embedding_status"),
        nullable=False,
        default="pending",
        index=True,
    )
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    file: Mapped["File"] = relationship("File", back_populates="chunks")
