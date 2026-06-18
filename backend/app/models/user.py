import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    provider: Mapped[str] = mapped_column(Enum("email", "google", "github", name="auth_provider"), default="email")
    provider_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String, nullable=True)
    two_factor_backup_codes: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSONB),
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    buckets: Mapped[list["Bucket"]] = relationship("Bucket", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", cascade="all, delete-orphan")
    oauth_tokens: Mapped[list["OAuthToken"]] = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme: Mapped[str] = mapped_column(Enum("light", "dark", name="theme_mode"), default="dark")
    language: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    preferred_llm: Mapped[str] = mapped_column(Enum("claude", "gemini", "gpt4o", "kimi", name="llm_provider"), default="claude")
    follow_up_mode: Mapped[str] = mapped_column(
        Enum("all_at_once", "one_by_one", name="follow_up_mode"),
        default="all_at_once",
    )
    use_case: Mapped[str | None] = mapped_column(Text, nullable=True)
    referral_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="profile")


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    access_token: Mapped[str | None] = mapped_column(String, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String, nullable=True)
    provider: Mapped[str] = mapped_column(Enum("email", "google", "github", name="auth_provider"), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="oauth_tokens")
