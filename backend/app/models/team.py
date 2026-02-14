from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AddTeamMemberRequest(BaseModel):
    name: str
    real_email: str
    password: str
    color: str = "#2DFFB7"


class UpdateTeamMemberRequest(BaseModel):
    color: Optional[str] = None
    show_name: Optional[bool] = None
    is_active: Optional[bool] = None


class BucketPermissions(BaseModel):
    bucket_id: str
    can_view: bool = True
    can_chat: bool = False
    can_upload: bool = False
    can_delete: bool = False


class AssignBucketsRequest(BaseModel):
    permissions: List[BucketPermissions]


class TeamMemberResponse(BaseModel):
    id: str
    owner_id: str
    member_id: Optional[str] = None
    name: str
    real_email: str
    aiveilix_email: str
    color: str
    show_name: bool
    is_active: bool
    removed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    bucket_count: Optional[int] = None


class TeamBucketAccessResponse(BaseModel):
    id: str
    team_member_id: str
    bucket_id: str
    bucket_name: Optional[str] = None
    can_view: bool
    can_chat: bool
    can_upload: bool
    can_delete: bool
    created_at: datetime


class TeamActivityLogEntry(BaseModel):
    id: str
    owner_id: str
    member_id: Optional[str] = None
    team_member_id: Optional[str] = None
    bucket_id: Optional[str] = None
    action_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    member_color: Optional[str] = None
    member_name: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime


class TeamInfoResponse(BaseModel):
    is_team_member: bool
    owner_id: Optional[str] = None
    team_member_id: Optional[str] = None
    color: Optional[str] = None
    name: Optional[str] = None
    show_name: Optional[bool] = None
