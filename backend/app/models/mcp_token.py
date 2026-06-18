import secrets
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


def _generate_token() -> str:
    return f"mcp_{secrets.token_urlsafe(32)}"


def _generate_account_token() -> str:
    return f"acct_{secrets.token_urlsafe(32)}"


class BucketMcpToken(Base):
    __tablename__ = "bucket_mcp_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, default=_generate_token)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Default Token")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Which of the 6 tools are enabled for this token
    # ["search", "query", "list_files", "get_file", "get_layout", "get_bucket_info"]
    allowed_tools: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=lambda: ["search", "query", "list_files", "get_file", "get_layout", "get_bucket_info"],
    )

    # Allowed origins — empty list means all origins allowed
    allowed_origins: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    logs: Mapped[list["McpAccessLog"]] = relationship("McpAccessLog", back_populates="token", cascade="all, delete-orphan")


class McpAccessLog(Base):
    __tablename__ = "mcp_access_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bucket_mcp_tokens.id", ondelete="CASCADE"), nullable=False, index=True)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    tool: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")  # success | error | forbidden
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    token: Mapped["BucketMcpToken"] = relationship("BucketMcpToken", back_populates="logs")


class AccountMcpToken(Base):
    """
    Account-level MCP token — one MCP URL that can reach multiple buckets.

    bucket_mode:
      "all"      — every bucket the user owns, including future ones
      "selected" — only the buckets listed in allowed_bucket_ids; buckets
                   created through this token are appended automatically
                   (an empty list means the token starts with no bucket access)
    """

    __tablename__ = "account_mcp_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, default=_generate_account_token)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Account MCP")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    bucket_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="all")  # all | selected
    allowed_bucket_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
