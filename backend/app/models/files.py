from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileUploadResponse(BaseModel):
    id: str
    name: str
    status: str
    message: Optional[str] = None


class CreateFileRequest(BaseModel):
    name: str
    content: str


class FileContentUpdateRequest(BaseModel):
    content: str


class FileResponse(BaseModel):
    id: str
    bucket_id: str
    name: str
    original_name: str
    mime_type: str
    size_bytes: int
    status: str
    status_message: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    folder_path: Optional[str] = None
    source: Optional[str] = None
    uploaded_by_color: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FilesListResponse(BaseModel):
    files: list[FileResponse]
    total: int


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    sources: Optional[list] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    mode: Optional[str] = None
    file_name_hint: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    sources: list
    conversation_id: str


class SummaryUpdateRequest(BaseModel):
    content: str


class SearchResult(BaseModel):
    file_id: str
    file_name: str
    match_type: str  # 'chunk', 'summary', 'filename', 'semantic', 'keyword'
    content: str
    chunk_id: Optional[str] = None
    summary_id: Optional[str] = None
    relevance_score: Optional[float] = None  # Similarity score for semantic search (0-1)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


class FilesBatchUploadResponse(BaseModel):
    results: list[FileUploadResponse]
    total: int
    successful: int
    failed: int
