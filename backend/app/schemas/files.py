import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel


# ---------- Upload ----------

class FileUploadResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    size: int
    status: str
    bucket_id: uuid.UUID
    r2_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- File Detail ----------

class FileResponse(BaseModel):
    id: uuid.UUID
    bucket_id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID | None
    name: str
    type: str
    size: int
    r2_path: str
    layout_json_path: str | None
    status: str
    page_count: int
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- File List ----------

class FileListResponse(BaseModel):
    files: list[FileResponse]
    total: int


# ---------- Layout ----------

class LayoutResponse(BaseModel):
    file_id: uuid.UUID
    layout_json_path: str | None
    layout: dict[str, Any] | None


# ---------- Chunks ----------

class ChunkResponse(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    bucket_id: uuid.UUID
    page: int
    content: str
    block_id: str
    nearby_image_id: str | None
    token_count: int
    status: str
    retry_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChunkListResponse(BaseModel):
    chunks: list[ChunkResponse]
    total: int


# ---------- Investigation Events ----------

class InvestigationEventResponse(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    event: str
    status: str
    event_metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class InvestigationEventListResponse(BaseModel):
    events: list[InvestigationEventResponse]
    total: int


# ---------- Retry ----------

class RetryResponse(BaseModel):
    message: str
    file_id: uuid.UUID


# ---------- Delete ----------

class DeleteFileResponse(BaseModel):
    message: str
    file_id: uuid.UUID
