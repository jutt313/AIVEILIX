import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


TeamMemberStatus = Literal["pending", "accepted", "rejected"]

TEAM_COLOR_PALETTE = [
    "#3B82F6",  # blue
    "#10B981",  # emerald
    "#8B5CF6",  # violet
    "#EC4899",  # pink
    "#F59E0B",  # amber
    "#14B8A6",  # teal
    "#EF4444",  # red
    "#6366F1",  # indigo
    "#EAB308",  # yellow
    "#06B6D4",  # cyan
    "#F43F5E",  # rose
    "#84CC16",  # lime
]


HistoryScope = Literal["from_now", "all"]


class BucketPermissionToggles(BaseModel):
    history_scope: HistoryScope = "from_now"
    can_see_other_members: bool = False
    can_upload_files: bool = False
    can_download_files: bool = False
    can_delete_files: bool = False
    can_use_mcp: bool = False


class BucketAccessGrantRequest(BaseModel):
    bucket_id: uuid.UUID
    permissions: BucketPermissionToggles = Field(default_factory=BucketPermissionToggles)


class TeamMemberInviteRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=120)
    display_color: str = Field(min_length=4, max_length=7)
    note: str | None = Field(default=None, max_length=1000)
    buckets: list[BucketAccessGrantRequest] = Field(default_factory=list)

    @field_validator("display_color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if not value.startswith("#") or len(value) not in (4, 7):
            raise ValueError("display_color must be a hex color like #RRGGBB")
        return value


class TeamMemberUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    display_color: str | None = Field(default=None, min_length=4, max_length=7)

    @field_validator("display_color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.startswith("#") or len(value) not in (4, 7):
            raise ValueError("display_color must be a hex color like #RRGGBB")
        return value


class BucketAccessResponse(BaseModel):
    id: uuid.UUID
    bucket_id: uuid.UUID
    team_member_id: uuid.UUID
    history_scope: HistoryScope
    can_see_other_members: bool
    can_upload_files: bool
    can_download_files: bool
    can_delete_files: bool
    can_use_mcp: bool
    granted_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class BucketAccessSummary(BaseModel):
    bucket_id: uuid.UUID
    bucket_name: str | None = None
    permissions: BucketPermissionToggles


class TeamMemberResponse(BaseModel):
    id: uuid.UUID
    owner_user_id: uuid.UUID
    member_user_id: uuid.UUID | None
    invited_by_user_id: uuid.UUID | None
    display_name: str | None
    display_color: str | None
    invite_email: str | None
    avatar_url: str | None = None
    status: TeamMemberStatus
    accepted_at: datetime | None
    last_active_at: datetime | None = None
    last_login_at: datetime | None = None
    is_online: bool = False
    created_at: datetime
    buckets: list[BucketAccessSummary] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class TeamActivityItem(BaseModel):
    id: str
    kind: Literal["joined", "invited", "sent_message", "created_thread"]
    team_member_id: uuid.UUID | None
    display_name: str | None
    display_color: str | None
    avatar_url: str | None = None
    bucket_id: uuid.UUID | None = None
    bucket_name: str | None = None
    conversation_id: uuid.UUID | None = None
    conversation_title: str | None = None
    snippet: str | None = None
    created_at: datetime


class TeamActivityResponse(BaseModel):
    items: list[TeamActivityItem]
    online_member_ids: list[uuid.UUID] = Field(default_factory=list)


class TeamMemberListResponse(BaseModel):
    members: list[TeamMemberResponse]
    total: int


class BucketAccessGrant(BaseModel):
    team_member_id: uuid.UUID
    permissions: BucketPermissionToggles = Field(default_factory=BucketPermissionToggles)


class BucketAccessUpdate(BaseModel):
    permissions: BucketPermissionToggles


class BucketAccessMemberInfo(BaseModel):
    team_member_id: uuid.UUID
    display_name: str | None
    display_color: str | None
    invite_email: str | None
    status: TeamMemberStatus
    permissions: BucketPermissionToggles
    granted_at: datetime


class BucketAccessListResponse(BaseModel):
    bucket_id: uuid.UUID
    members: list[BucketAccessMemberInfo]


class InviteValidateResponse(BaseModel):
    valid: bool
    expired: bool = False
    already_accepted: bool = False
    workspace_owner_name: str | None = None
    workspace_owner_email: str | None = None
    invite_email: str | None = None
    display_name: str | None = None
    display_color: str | None = None
    expires_at: datetime | None = None


class InviteAcceptRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)


class InviteAcceptResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    team_member_id: uuid.UUID
    workspace_owner_id: uuid.UUID
