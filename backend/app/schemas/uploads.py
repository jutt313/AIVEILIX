"""Schemas for the direct-to-R2 upload session flow.

Flow:
  init     → backend checks plan/quota, mints a file_id + R2 key, returns either
             a single presigned PUT URL or a multipart upload id + part size.
  parts    → backend returns presigned URLs for the requested part numbers.
  complete → backend completes multipart (if any), HEADs + verifies the object,
             then creates the files/file_versions rows and starts processing.
  abort    → backend marks the session aborted and aborts any R2 multipart.
"""

import uuid

from pydantic import BaseModel, Field


class UploadInitRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=500)
    content_type: str | None = Field(default=None, max_length=255)
    size: int = Field(..., ge=0)


class UploadInitResponse(BaseModel):
    mode: str                 # "single" | "multipart"
    upload_id: uuid.UUID      # app upload-session id (used in subsequent calls)
    file_id: uuid.UUID        # id the resulting files row will use
    r2_key: str
    expires_in: int
    # single mode only
    url: str | None = None
    # multipart mode only
    r2_upload_id: str | None = None
    part_size: int | None = None
    part_count: int | None = None


class UploadPartsRequest(BaseModel):
    part_numbers: list[int] = Field(..., min_length=1)


class UploadPartUrl(BaseModel):
    part_number: int
    url: str


class UploadPartsResponse(BaseModel):
    parts: list[UploadPartUrl]


class CompletedPart(BaseModel):
    # Field names match the S3/R2 CompleteMultipartUpload contract.
    PartNumber: int = Field(..., ge=1)
    ETag: str


class UploadCompleteRequest(BaseModel):
    parts: list[CompletedPart] = Field(default_factory=list)


class UploadAbortResponse(BaseModel):
    status: str
    upload_id: uuid.UUID
