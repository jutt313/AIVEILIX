from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MCPQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    max_results: Optional[int] = Field(default=10, ge=1, le=100, description="Maximum number of results")


class MCPChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="Chat message")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation ID for context")


class MCPBucketResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    file_count: int
    total_size_bytes: int
    created_at: datetime


class MCPBucketsListResponse(BaseModel):
    buckets: List[MCPBucketResponse]
    total: int


class MCPFileResponse(BaseModel):
    id: str
    name: str
    status: str
    status_message: Optional[str] = None
    word_count: Optional[int] = None
    size_bytes: int
    created_at: datetime


class MCPFilesListResponse(BaseModel):
    files: List[MCPFileResponse]
    total: int


class MCPQueryResult(BaseModel):
    file_id: str
    file_name: str
    content: str
    relevance_score: float
    chunk_id: Optional[str] = None


class MCPQueryResponse(BaseModel):
    results: List[MCPQueryResult]
    total: int
    query: str


class MCPSource(BaseModel):
    file_name: str
    file_id: str
    type: str  # 'chunk' or 'analysis'
    chunk_id: Optional[str] = None
    summary_id: Optional[str] = None


class MCPChatResponse(BaseModel):
    response: str
    sources: List[MCPSource]
    conversation_id: str


class MCPErrorResponse(BaseModel):
    error: str
    code: str
    message: Optional[str] = None
