from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CreateAPIKeyRequest(BaseModel):
    name: str
    scopes: List[str] = ["read"]  # ['read', 'write', 'delete']
    allowed_buckets: Optional[List[str]] = None  # If None, access to all buckets


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str  # Only prefix shown, never full key
    scopes: List[str]
    allowed_buckets: Optional[List[str]]
    is_active: bool
    last_used_at: Optional[datetime]
    request_count: int
    created_at: datetime


class CreateAPIKeyResponse(BaseModel):
    success: bool
    message: str
    api_key: Optional[str] = None  # Full key shown ONLY once on creation
    key_data: Optional[APIKeyResponse] = None


class APIKeysListResponse(BaseModel):
    keys: List[APIKeyResponse]
    total: int
