import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


WebSearchMode = Literal["smart", "bucket_only", "always_search"]
FollowUpMode = Literal["all_at_once", "one_by_one"]
MessageRole = Literal["user", "assistant"]


class ConversationCreateRequest(BaseModel):
    title: str | None = None
    web_search_mode: WebSearchMode = "smart"
    follow_up_mode: FollowUpMode | None = None


class ConversationUpdateRequest(BaseModel):
    title: str | None = None
    web_search_mode: WebSearchMode | None = None
    follow_up_mode: FollowUpMode | None = None


class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    bucket_id: uuid.UUID
    title: str
    web_search_mode: WebSearchMode
    follow_up_mode: FollowUpMode
    is_pinned: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class SourceItem(BaseModel):
    kind: Literal["document", "web", "memory", "general"]
    label: str
    file_id: uuid.UUID | None = None
    chunk_id: uuid.UUID | None = None
    page: int | None = None
    url: str | None = None
    score: float | None = None


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)
    web_search: bool | None = None  # If set, overrides conversation web_search_mode for this turn
    agentic_mode: bool | None = None  # If true, use the deeper bounded agent loop for this turn


class MessageSender(BaseModel):
    kind: Literal["owner", "team_member", "team_member_hidden", "assistant"]
    display_name: str | None = None
    display_color: str | None = None
    team_member_id: uuid.UUID | None = None


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    parent_message_id: uuid.UUID | None
    role: MessageRole
    content: str
    chunks_used: list[dict]
    token_count: int
    embedding_status: str
    agent_plan: list[dict] | None = None
    agent_steps: list[dict] | None = None
    sender_team_member_id: uuid.UUID | None = None
    sender: MessageSender | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int


class AgentReplyResponse(BaseModel):
    conversation: ConversationResponse
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: list[SourceItem]
    used_web_search: bool
    follow_up_required: bool = False
    action_required: bool = False
    action_type: str | None = None          # e.g. "web_search_permission", "save_file", "clarify"
    action_options: list[str] | None = None  # button labels shown in frontend
    thinking_steps: list[str] | None = None  # plain-text step labels (back-compat)
    thinking_step_events: list[dict] | None = None  # typed step events: {type, label, tool?}
    plan: list[dict] | None = None           # harness TODO list (16px checklist on the frontend)


class DeleteConversationResponse(BaseModel):
    message: str
    conversation_id: uuid.UUID


class BucketSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=25)
    conversation_id: uuid.UUID | None = None


class BucketSearchResult(BaseModel):
    chunk_id: uuid.UUID
    file_id: uuid.UUID
    file_name: str
    page: int
    content: str
    score: float


class BucketSearchResponse(BaseModel):
    results: list[BucketSearchResult]
    total: int


class BucketQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    conversation_id: uuid.UUID | None = None


class BucketQueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    used_web_search: bool
    follow_up_required: bool = False


class MessageFeedbackRequest(BaseModel):
    rating: Literal["like", "dislike"]
    reason: str | None = None


class MessageFeedbackResponse(BaseModel):
    message_id: uuid.UUID
    rating: str
    reason: str | None = None
