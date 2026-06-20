import uuid
from datetime import datetime

from sqlalchemy import Boolean, BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Bucket(Base):
    __tablename__ = "buckets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    mcp_url: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    mcp_token: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#3B82F6")
    icon: Mapped[str] = mapped_column(String(50), nullable=False, default="folder")
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Demo buckets back a public /try/:slug page. They are hidden from the normal
    # dashboard and never count against the owning (admin) account's plan quota.
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    storage_used: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    categories: Mapped[list["Category"]] = relationship("Category", back_populates="bucket", cascade="all, delete-orphan")
    files: Mapped[list["File"]] = relationship("File", back_populates="bucket", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="bucket", cascade="all, delete-orphan")
    summaries: Mapped[list["Summary"]] = relationship("Summary", back_populates="bucket")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#3B82F6")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    bucket: Mapped["Bucket"] = relationship("Bucket", back_populates="categories")
    files: Mapped[list["File"]] = relationship("File", back_populates="category")
