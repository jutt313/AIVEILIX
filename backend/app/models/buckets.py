from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeleteAllBucketsRequest(BaseModel):
    password: str


class BucketCreate(BaseModel):
    name: str
    description: Optional[str] = None


class BucketResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    is_private: bool
    file_count: int
    total_size_bytes: int
    created_at: datetime
    updated_at: datetime


class BucketsListResponse(BaseModel):
    buckets: list[BucketResponse]
    total: int


class DashboardStats(BaseModel):
    total_buckets: int
    total_files: int
    total_storage_bytes: int


class ActivityDataPoint(BaseModel):
    date: str
    files: int
    buckets: int
    storage: float  # in MB


class ActivityDataResponse(BaseModel):
    data: list[ActivityDataPoint]
