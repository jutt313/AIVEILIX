"""
MCP Protocol Server for AIveilix

Implements the Model Context Protocol (MCP) using the official Python SDK.
Provides both TOOLS (for ChatGPT/Claude) and RESOURCES (for Cursor) to access knowledge buckets.

Transports supported:
- HTTP/SSE (for ChatGPT via /mcp endpoint)
- Stdio (for Cursor via mcp_stdio.py entry point)

MCP Resources (for Cursor):
- aiveilix://buckets - List all buckets
- aiveilix://buckets/{id} - Bucket details with files
- aiveilix://buckets/{id}/files - Files list
- aiveilix://buckets/{id}/search?q={query} - Search results

MCP Tools (for ChatGPT/Claude):
- list_buckets, list_bucket_files, query_bucket, chat_bucket, get_bucket_info
"""
import logging
import json
import re
import asyncio
import time
from typing import Any, Optional, List
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Response, HTTPException, Depends, Header, Form
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.mcp_auth import get_mcp_user, check_bucket_access_mcp, MCPAuthError
from app.utils.error_logger import log_error, get_correlation_id, log_request_with_timing
from app.services.mcp_services import (
    list_buckets_service,
    list_files_service,
    query_bucket_service,
    chat_bucket_service,
    get_bucket_info_service,
    get_file_content_service,
    MCPServiceError,
)
from app.services.oauth2 import get_oauth2_service
from app.models.oauth import (
    OAuthAuthorizeRequest,
    OAuthTokenRequest,
    OAuthTokenResponse,
    OAuthClientCreate,
    OAuthClientResponse,
    OAuthClientInfo,
    MCPUser,
)

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== MCP Protocol Types ====================

class MCPToolInput(BaseModel):
    """Base model for MCP tool input"""
    pass


class ListBucketsInput(MCPToolInput):
    """Input for list_buckets tool"""
    pass


class ListFilesInput(MCPToolInput):
    """Input for list_bucket_files tool"""
    bucket_id: str = Field(..., description="UUID of the bucket to list files from")


class QueryBucketInput(MCPToolInput):
    """Input for query_bucket tool"""
    bucket_id: str = Field(..., description="UUID of the bucket to query")
    query: str = Field(..., description="Search query text")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of results")


class ChatBucketInput(MCPToolInput):
    """Input for chat_bucket tool"""
    bucket_id: str = Field(..., description="UUID of the bucket to chat with")
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation ID for context")


class GetBucketInfoInput(MCPToolInput):
    """Input for get_bucket_info tool"""
    bucket_id: str = Field(..., description="UUID of the bucket to get info for")


# ==================== MCP Tool Definitions ====================

MCP_TOOLS = [
    {
        "name": "list_buckets",
        "description": "List all knowledge buckets accessible to the user. Returns bucket names, descriptions, file counts, and sizes.",
        "visibility": "public",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "list_bucket_files",
        "description": "List all files in a specific bucket. Returns file names, processing status, word counts, and sizes.",
        "visibility": "public",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bucket_id": {
                    "type": "string",
                    "description": "UUID of the bucket to list files from"
                }
            },
            "required": ["bucket_id"]
        }
    },
    {
        "name": "query_bucket",
        "description": "Search/query bucket content using semantic search. Returns relevant chunks from files matching the query.",
        "visibility": "public",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bucket_id": {
                    "type": "string",
                    "description": "UUID of the bucket to query"
                },
                "query": {
                    "type": "string",
                    "description": "Search query text"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (1-100, default 10)",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["bucket_id", "query"]
        }
    },
    {
        "name": "chat_bucket",
        "description": "Chat with a knowledge bucket using AI. The AI has access to all file content and analysis in the bucket and can answer questions about them.",
        "visibility": "public",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bucket_id": {
                    "type": "string",
                    "description": "UUID of the bucket to chat with"
                },
                "message": {
                    "type": "string",
                    "description": "User message/question"
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Optional conversation ID for maintaining context across messages"
                }
            },
            "required": ["bucket_id", "message"]
        }
    },
    {
        "name": "get_bucket_info",
        "description": "Get detailed information about a specific bucket including file status breakdown.",
        "visibility": "public",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bucket_id": {
                    "type": "string",
                    "description": "UUID of the bucket to get info for"
                }
            },
            "required": ["bucket_id"]
        }
    },
    {
        "name": "get_file_content",
        "description": "Get the full extracted text content, summary, and optionally raw data for a specific file. Use this to read the actual content of documents, images, PDFs, and code files stored in a bucket.",
        "visibility": "public",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bucket_id": {
                    "type": "string",
                    "description": "UUID of the bucket containing the file"
                },
                "file_id": {
                    "type": "string",
                    "description": "UUID of the file to get content for"
                },
                "include_raw": {
                    "type": "boolean",
                    "description": "If true, include base64-encoded raw data for image files (default: false)",
                    "default": False
                }
            },
            "required": ["bucket_id", "file_id"]
        }
    }
]


# ==================== MCP Protocol Handlers ====================

class MCPProtocolHandler:
    """Handler for MCP JSON-RPC protocol messages"""

    def __init__(self, user: MCPUser):
        self.user = user

    async def handle_message(self, message: dict) -> dict:
        """Handle a JSON-RPC message and return response with detailed error tracking"""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        handler_start = time.time()
        logger.info(f"MCPProtocolHandler - Handling message: method={method}, id={msg_id}, params_keys={list(params.keys()) if params else []}, user_id={self.user.user_id}")

        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list()
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list()
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            elif method == "prompts/list":
                result = await self.handle_prompts_list()
            elif method == "ping":
                result = {}
            else:
                logger.warning(f"MCPProtocolHandler - Unknown method: {method}, user_id={self.user.user_id}")
                return self._error_response(msg_id, -32601, f"Method not found: {method}")

            handler_duration = (time.time() - handler_start) * 1000
            logger.info(f"MCPProtocolHandler - Successfully handled {method}, duration={handler_duration:.2f}ms, result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
            return self._success_response(msg_id, result)

        except MCPServiceError as e:
            handler_duration = (time.time() - handler_start) * 1000
            logger.error(f"MCPProtocolHandler - Service error: {e.message}, code: {e.code}, duration={handler_duration:.2f}ms, method={method}, user_id={self.user.user_id}")
            return self._error_response(msg_id, -32000, e.message, {"code": e.code})
        except HTTPException as e:
            handler_duration = (time.time() - handler_start) * 1000
            logger.error(f"MCPProtocolHandler - HTTP exception: {e.detail}, status: {e.status_code}, duration={handler_duration:.2f}ms, method={method}, user_id={self.user.user_id}")
            return self._error_response(msg_id, -32000, str(e.detail))
        except Exception as e:
            handler_duration = (time.time() - handler_start) * 1000
            logger.error(f"MCPProtocolHandler - Unexpected error: {e}, duration={handler_duration:.2f}ms, method={method}, user_id={self.user.user_id}", exc_info=True)
            return self._error_response(msg_id, -32603, f"Internal error: {str(e)}")

    async def handle_initialize(self, params: dict) -> dict:
        """Handle initialize request"""
        # Get base URL from request if available (for OAuth endpoints)
        # Note: params might not have request, so we'll use relative paths
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": True},  # Resources enabled!
                "prompts": {"listChanged": False},
            },
            "serverInfo": {
                "name": settings.mcp_server_name,
                "version": settings.mcp_server_version,
                "description": "AIveilix Knowledge Bucket MCP Server - Access your documents via Tools or Resources",
            }
        }

    async def handle_tools_list(self) -> dict:
        """Handle tools/list request"""
        return {"tools": MCP_TOOLS}

    async def handle_tools_call(self, params: dict) -> dict:
        """Handle tools/call request with detailed timing"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        tool_start = time.time()
        logger.info(f"MCPProtocolHandler - Tool call START: {tool_name}, arguments_keys={list(arguments.keys()) if arguments else []}, user_id={self.user.user_id}")

        try:
            if tool_name == "list_buckets":
                result = await self._call_list_buckets()
            elif tool_name == "list_bucket_files":
                result = await self._call_list_files(arguments)
            elif tool_name == "query_bucket":
                result = await self._call_query_bucket(arguments)
            elif tool_name == "chat_bucket":
                result = await self._call_chat_bucket(arguments)
            elif tool_name == "get_bucket_info":
                result = await self._call_get_bucket_info(arguments)
            elif tool_name == "get_file_content":
                result = await self._call_get_file_content(arguments)
            else:
                raise MCPServiceError(f"Unknown tool: {tool_name}", "unknown_tool")
            
            tool_duration = (time.time() - tool_start) * 1000
            
            # Log slow tool calls
            if tool_duration > 3000:
                logger.warning(f"MCPProtocolHandler - Slow tool call: {tool_name}, duration={tool_duration:.2f}ms, user_id={self.user.user_id}")
            else:
                logger.info(f"MCPProtocolHandler - Tool call SUCCESS: {tool_name}, duration={tool_duration:.2f}ms")
            
            return result
            
        except Exception as e:
            tool_duration = (time.time() - tool_start) * 1000
            logger.error(f"MCPProtocolHandler - Tool call ERROR: {tool_name}, duration={tool_duration:.2f}ms, error={str(e)}, user_id={self.user.user_id}", exc_info=True)
            raise

    async def handle_resources_list(self) -> dict:
        """
        Handle resources/list request.
        Exposes buckets as MCP resources for Cursor and other resource-based clients.
        """
        resources = []
        
        try:
            # Get user's buckets
            buckets = await list_buckets_service(self.user)
            
            # Add root buckets list resource
            resources.append({
                "uri": "aiveilix://buckets",
                "name": "All Buckets",
                "description": f"List of all {len(buckets)} knowledge buckets",
                "mimeType": "application/json"
            })
            
            # Add each bucket as a resource
            for bucket in buckets:
                # Bucket info resource
                resources.append({
                    "uri": f"aiveilix://buckets/{bucket.id}",
                    "name": bucket.name,
                    "description": bucket.description or f"Bucket with {bucket.file_count} files",
                    "mimeType": "application/json"
                })
                
                # Bucket files resource
                resources.append({
                    "uri": f"aiveilix://buckets/{bucket.id}/files",
                    "name": f"{bucket.name} - Files",
                    "description": f"Files in {bucket.name} ({bucket.file_count} files)",
                    "mimeType": "application/json"
                })
                
                # Bucket search resource (template)
                resources.append({
                    "uri": f"aiveilix://buckets/{bucket.id}/search",
                    "name": f"{bucket.name} - Search",
                    "description": f"Search in {bucket.name}. Append ?q=your_query to search.",
                    "mimeType": "application/json"
                })
            
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
        
        return {"resources": resources}

    async def handle_resources_read(self, params: dict) -> dict:
        """
        Handle resources/read request.
        Reads content from an MCP resource URI.
        """
        uri = params.get("uri", "")
        
        if not uri.startswith("aiveilix://"):
            raise MCPServiceError(f"Unknown resource URI scheme: {uri}", "invalid_uri")
        
        # Parse the URI
        path = uri.replace("aiveilix://", "")
        
        # Handle query parameters
        query_params = {}
        if "?" in path:
            path, query_string = path.split("?", 1)
            query_params = parse_qs(query_string)
        
        parts = path.strip("/").split("/")
        
        try:
            # Route: aiveilix://buckets
            if path == "buckets" or path == "buckets/":
                return await self._read_buckets_list()
            
            # Route: aiveilix://buckets/{id}
            elif len(parts) == 2 and parts[0] == "buckets":
                bucket_id = parts[1]
                await check_bucket_access_mcp(self.user, bucket_id)
                return await self._read_bucket_info(bucket_id)
            
            # Route: aiveilix://buckets/{id}/files
            elif len(parts) == 3 and parts[0] == "buckets" and parts[2] == "files":
                bucket_id = parts[1]
                await check_bucket_access_mcp(self.user, bucket_id)
                return await self._read_bucket_files(bucket_id)
            
            # Route: aiveilix://buckets/{id}/search?q=query
            elif len(parts) == 3 and parts[0] == "buckets" and parts[2] == "search":
                bucket_id = parts[1]
                query = query_params.get("q", [""])[0]
                if not query:
                    return {
                        "contents": [{
                            "uri": uri,
                            "mimeType": "text/plain",
                            "text": "Please provide a search query using ?q=your_query"
                        }]
                    }
                await check_bucket_access_mcp(self.user, bucket_id)
                return await self._read_bucket_search(bucket_id, query)
            
            else:
                raise MCPServiceError(f"Unknown resource path: {path}", "not_found")
                
        except HTTPException as e:
            raise MCPServiceError(str(e.detail), "access_denied")

    async def _read_buckets_list(self) -> dict:
        """Read all buckets as resource content"""
        buckets = await list_buckets_service(self.user)
        
        content = "# Your Knowledge Buckets\n\n"
        for bucket in buckets:
            content += f"## {bucket.name}\n"
            content += f"- **ID**: `{bucket.id}`\n"
            content += f"- **Description**: {bucket.description or 'No description'}\n"
            content += f"- **Files**: {bucket.file_count}\n"
            content += f"- **Size**: {bucket.total_size_bytes:,} bytes\n"
            content += f"- **Created**: {bucket.created_at}\n\n"
        
        if not buckets:
            content += "_No buckets found._\n"
        
        return {
            "contents": [{
                "uri": "aiveilix://buckets",
                "mimeType": "text/markdown",
                "text": content
            }]
        }

    async def _read_bucket_info(self, bucket_id: str) -> dict:
        """Read bucket info as resource content"""
        info = await get_bucket_info_service(bucket_id, self.user)
        files = await list_files_service(bucket_id, self.user)
        
        content = f"# {info['name']}\n\n"
        content += f"**ID**: `{info['id']}`\n\n"
        content += f"**Description**: {info['description'] or 'No description'}\n\n"
        content += f"**Total Files**: {info['file_count']}\n\n"
        content += f"**Total Size**: {info['total_size_bytes']:,} bytes\n\n"
        content += f"**Created**: {info['created_at']}\n\n"
        
        # File status breakdown
        content += "## File Status\n"
        for status, count in info['file_status_breakdown'].items():
            content += f"- {status}: {count}\n"
        
        # List files
        content += f"\n## Files ({len(files)})\n\n"
        for f in files[:50]:  # Limit to 50 files
            status_icon = "✅" if f.status == "ready" else "⏳" if f.status == "processing" else "❌"
            content += f"- {status_icon} **{f.name}** ({f.size_bytes:,} bytes)\n"
        
        if len(files) > 50:
            content += f"\n_...and {len(files) - 50} more files_\n"
        
        return {
            "contents": [{
                "uri": f"aiveilix://buckets/{bucket_id}",
                "mimeType": "text/markdown",
                "text": content
            }]
        }

    async def _read_bucket_files(self, bucket_id: str) -> dict:
        """Read bucket files as resource content"""
        files = await list_files_service(bucket_id, self.user)
        
        content = "# Files\n\n"
        content += "| Name | Status | Words | Size |\n"
        content += "|------|--------|-------|------|\n"
        
        for f in files:
            status_icon = "✅" if f.status == "ready" else "⏳" if f.status == "processing" else "❌"
            words = f.word_count if f.word_count else "-"
            content += f"| {f.name} | {status_icon} {f.status} | {words} | {f.size_bytes:,} |\n"
        
        if not files:
            content += "| _No files_ | - | - | - |\n"
        
        return {
            "contents": [{
                "uri": f"aiveilix://buckets/{bucket_id}/files",
                "mimeType": "text/markdown",
                "text": content
            }]
        }

    async def _read_bucket_search(self, bucket_id: str, query: str) -> dict:
        """Read bucket search results as resource content"""
        result = await query_bucket_service(bucket_id, query, self.user, max_results=10)
        
        content = f"# Search Results for \"{query}\"\n\n"
        content += f"Found **{result['total']}** results\n\n"
        
        for i, r in enumerate(result['results'], 1):
            content += f"## Result {i}: {r.file_name}\n"
            content += f"**Relevance**: {r.relevance_score:.2f}\n\n"
            content += f"```\n{r.content[:500]}{'...' if len(r.content) > 500 else ''}\n```\n\n"
        
        if result['total'] == 0:
            content += "_No results found for this query._\n"
        
        return {
            "contents": [{
                "uri": f"aiveilix://buckets/{bucket_id}/search?q={query}",
                "mimeType": "text/markdown",
                "text": content
            }]
        }

    async def handle_prompts_list(self) -> dict:
        """Handle prompts/list request (optional)"""
        return {"prompts": []}

    # ==================== Tool Implementations ====================

    async def _call_list_buckets(self) -> dict:
        """Execute list_buckets tool"""
        buckets = await list_buckets_service(self.user)
        
        content = []
        for bucket in buckets:
            content.append({
                "type": "text",
                "text": f"**{bucket.name}** (ID: {bucket.id})\n"
                       f"  Description: {bucket.description or 'No description'}\n"
                       f"  Files: {bucket.file_count}, Size: {bucket.total_size_bytes} bytes"
            })
        
        if not content:
            content = [{"type": "text", "text": "No buckets found."}]
        
        return {
            "content": content,
            "isError": False
        }

    async def _call_list_files(self, arguments: dict) -> dict:
        """Execute list_bucket_files tool"""
        bucket_id = arguments.get("bucket_id")
        if not bucket_id:
            raise MCPServiceError("bucket_id is required", "missing_parameter")
        
        # Check bucket access
        await check_bucket_access_mcp(self.user, bucket_id)
        
        files = await list_files_service(bucket_id, self.user)
        
        content = []
        for file in files:
            status_info = f"Status: {file.status}"
            if file.status_message:
                status_info += f" ({file.status_message})"
            
            content.append({
                "type": "text",
                "text": f"**{file.name}** (ID: {file.id})\n"
                       f"  {status_info}\n"
                       f"  Words: {file.word_count or 'N/A'}, Size: {file.size_bytes} bytes"
            })
        
        if not content:
            content = [{"type": "text", "text": "No files found in this bucket."}]
        
        return {
            "content": content,
            "isError": False
        }

    async def _call_query_bucket(self, arguments: dict) -> dict:
        """Execute query_bucket tool with detailed timing"""
        bucket_id = arguments.get("bucket_id")
        query = arguments.get("query")
        max_results = arguments.get("max_results", 10)
        
        if not bucket_id:
            raise MCPServiceError("bucket_id is required", "missing_parameter")
        if not query:
            raise MCPServiceError("query is required", "missing_parameter")
        
        query_start = time.time()
        logger.info(f"MCPProtocolHandler - Query bucket START: bucket_id={bucket_id}, query_length={len(query)}, max_results={max_results}, user_id={self.user.user_id}")
        
        # Check bucket access
        await check_bucket_access_mcp(self.user, bucket_id)
        
        # Execute query with timing
        service_start = time.time()
        result = await query_bucket_service(bucket_id, query, self.user, max_results)
        service_duration = (time.time() - service_start) * 1000
        total_duration = (time.time() - query_start) * 1000
        
        logger.info(f"MCPProtocolHandler - Query bucket SUCCESS: bucket_id={bucket_id}, results={result['total']}, service_duration={service_duration:.2f}ms, total_duration={total_duration:.2f}ms")
        
        content = []
        content.append({
            "type": "text",
            "text": f"Query: \"{result['query']}\"\nFound {result['total']} results:\n"
        })
        
        for i, r in enumerate(result['results'], 1):
            content.append({
                "type": "text",
                "text": f"\n**Result {i}** (File: {r.file_name}, Relevance: {r.relevance_score:.2f})\n{r.content}\n"
            })
        
        if result['total'] == 0:
            content = [{"type": "text", "text": f"No results found for query: \"{query}\""}]
        
        return {
            "content": content,
            "isError": False
        }

    async def _call_chat_bucket(self, arguments: dict) -> dict:
        """Execute chat_bucket tool with detailed timing"""
        bucket_id = arguments.get("bucket_id")
        message = arguments.get("message")
        conversation_id = arguments.get("conversation_id")
        
        if not bucket_id:
            raise MCPServiceError("bucket_id is required", "missing_parameter")
        if not message:
            raise MCPServiceError("message is required", "missing_parameter")
        
        chat_start = time.time()
        logger.info(f"MCPProtocolHandler - Chat bucket START: bucket_id={bucket_id}, message_length={len(message)}, conversation_id={conversation_id}, user_id={self.user.user_id}")
        
        # Check bucket access
        await check_bucket_access_mcp(self.user, bucket_id)
        
        # Execute chat with timing
        service_start = time.time()
        result = await chat_bucket_service(bucket_id, message, self.user, conversation_id)
        service_duration = (time.time() - service_start) * 1000
        total_duration = (time.time() - chat_start) * 1000
        
        logger.info(f"MCPProtocolHandler - Chat bucket SUCCESS: bucket_id={bucket_id}, response_length={len(result['response'])}, sources={len(result['sources'])}, service_duration={service_duration:.2f}ms, total_duration={total_duration:.2f}ms")
        
        # Build response content
        response_text = result['response']
        
        # Add source references if available
        if result['sources']:
            source_files = list(set(s.file_name for s in result['sources']))
            response_text += f"\n\n---\n*Sources: {', '.join(source_files)}*"
        
        # Add conversation ID for continuity
        response_text += f"\n*Conversation ID: {result['conversation_id']}*"
        
        return {
            "content": [{"type": "text", "text": response_text}],
            "isError": False
        }

    async def _call_get_bucket_info(self, arguments: dict) -> dict:
        """Execute get_bucket_info tool"""
        bucket_id = arguments.get("bucket_id")
        if not bucket_id:
            raise MCPServiceError("bucket_id is required", "missing_parameter")
        
        # Check bucket access
        await check_bucket_access_mcp(self.user, bucket_id)
        
        info = await get_bucket_info_service(bucket_id, self.user)
        
        status_breakdown = "\n".join(
            f"  - {status}: {count}" 
            for status, count in info['file_status_breakdown'].items()
        ) or "  No files"
        
        content = [{
            "type": "text",
            "text": f"**{info['name']}** (ID: {info['id']})\n"
                   f"Description: {info['description'] or 'No description'}\n"
                   f"Total Files: {info['file_count']}\n"
                   f"Total Size: {info['total_size_bytes']} bytes\n"
                   f"Created: {info['created_at']}\n"
                   f"\nFile Status Breakdown:\n{status_breakdown}"
        }]
        
        return {
            "content": content,
            "isError": False
        }

    async def _call_get_file_content(self, arguments: dict) -> dict:
        """Execute get_file_content tool"""
        bucket_id = arguments.get("bucket_id")
        file_id = arguments.get("file_id")
        include_raw = arguments.get("include_raw", False)

        if not bucket_id:
            raise MCPServiceError("bucket_id is required", "missing_parameter")
        if not file_id:
            raise MCPServiceError("file_id is required", "missing_parameter")

        # Check bucket access
        await check_bucket_access_mcp(self.user, bucket_id)

        result = await get_file_content_service(bucket_id, file_id, self.user, include_raw)

        content = []

        # File header
        header = (
            f"**{result['file_name']}** (ID: {result['file_id']})\n"
            f"Type: {result['mime_type']}, Size: {result['size_bytes']} bytes, "
            f"Words: {result.get('word_count') or 'N/A'}, "
            f"Chunks: {result.get('chunk_count', 0)}, Source: {result.get('source', 'unknown')}"
        )
        content.append({"type": "text", "text": header})

        # Summary
        if result.get("summary"):
            content.append({"type": "text", "text": f"\n**Summary:**\n{result['summary']}"})

        # Full text content
        if result.get("content"):
            text = result["content"]
            # Cap at 30k chars for MCP response
            if len(text) > 30000:
                text = text[:30000] + f"\n\n... [Truncated, {len(result['content'])} total chars]"
            content.append({"type": "text", "text": f"\n**Content:**\n{text}"})
        else:
            content.append({"type": "text", "text": "\nNo extracted text content available for this file."})

        # Raw image data
        if result.get("raw_base64"):
            content.append({
                "type": "image",
                "data": result["raw_base64"],
                "mimeType": result.get("raw_mime_type", "image/png")
            })

        return {
            "content": content,
            "isError": False
        }

    # ==================== Response Helpers ====================

    def _success_response(self, msg_id: Any, result: dict) -> dict:
        """Create JSON-RPC success response"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }

    def _error_response(self, msg_id: Any, code: int, message: str, data: dict = None) -> dict:
        """Create JSON-RPC error response"""
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": error
        }


# ==================== HTTP Transport Endpoints ====================

@router.post("/protocol")
async def mcp_protocol_endpoint(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    MCP Protocol endpoint for HTTP transport.
    Accepts JSON-RPC messages and returns responses.
    
    Supports discovery without auth, but requires auth for actual operations.
    """
    start_time = time.time()
    correlation_id = get_correlation_id(request)
    
    # Log incoming request details
    logger.info(f"MCP POST /protocol - Correlation ID: {correlation_id}, Headers: {dict(request.headers)}")
    logger.info(f"MCP POST /protocol - Authorization: {'Present' if authorization else 'Missing'}")
    
    # Try to authenticate if authorization header is provided
    user = None
    user_id = None
    if authorization:
        try:
            auth_start = time.time()
            user = await get_mcp_user(authorization, request)
            auth_duration = (time.time() - auth_start) * 1000
            user_id = user.user_id
            logger.info(f"MCP POST /protocol - Authentication successful: user_id={user.user_id}, auth_type={user.auth_type}, duration={auth_duration:.2f}ms")
        except MCPAuthError as e:
            auth_duration = (time.time() - auth_start) * 1000
            logger.error(f"MCP POST /protocol - Authentication failed: {e.detail}, status={e.status_code}, duration={auth_duration:.2f}ms")
            await log_error(
                request,
                e,
                correlation_id=correlation_id,
                request_duration_ms=auth_duration,
                additional_context={
                    "auth_method": "oauth" if "oauth" in str(e).lower() else "api_key",
                    "endpoint": "/mcp/server/protocol"
                }
            )
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32000, "message": str(e.detail)}
                },
                status_code=e.status_code
            )
    else:
        # No auth - check if this is a discovery request (initialize or tools/list)
        try:
            body = await request.json()
            method = body.get("method")
            logger.info(f"MCP POST /protocol - No auth, method={method}, body={body}")
            
            # Allow discovery methods without auth
            if method in ["initialize", "tools/list", "resources/list", "prompts/list"]:
                logger.info(f"MCP POST /protocol - Allowing discovery method: {method}")
                # Handle discovery methods directly without requiring auth
                if method == "initialize":
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {"listChanged": False},
                                "resources": {"subscribe": False, "listChanged": False},
                                "prompts": {"listChanged": False},
                            },
                            "serverInfo": {
                                "name": settings.mcp_server_name,
                                "version": settings.mcp_server_version,
                            }
                        }
                    })
                elif method == "tools/list":
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {"tools": MCP_TOOLS}
                    })
                else:
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {"resources": []} if method == "resources/list" else {"prompts": []}
                    })
            else:
                # Other methods require auth
                logger.warning(f"MCP POST /protocol - Method {method} requires auth but none provided")
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id") if isinstance(body, dict) else None,
                        "error": {"code": -32000, "message": "Authentication required. Use Authorization: Bearer <api_key> header."}
                    },
                    status_code=401
                )
        except json.JSONDecodeError as e:
            # Invalid JSON - return server info for discovery
            logger.error(f"MCP POST /protocol - JSON decode error: {e}, body={await request.body()}")
            return JSONResponse(
                content={
                    "name": settings.mcp_server_name,
                    "version": settings.mcp_server_version,
                    "protocol_version": "2024-11-05",
                    "capabilities": {"tools": True, "resources": False, "prompts": False},
                    "authentication": {"oauth2": True, "api_key": True},
                    "message": "Authentication required. Use Authorization: Bearer <api_key> header."
                }
            )
        except Exception as e:
            logger.error(f"MCP POST /protocol - Unexpected error: {e}", exc_info=True)
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32000, "message": f"Authentication required. Error: {str(e)}"}
                },
                status_code=401
            )
    
    # Authenticated requests - process normally
    if not user:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"MCP POST /protocol - No user after auth check, correlation_id={correlation_id}")
        error = Exception("No user after auth check")
        await log_error(
            request,
            error,
            correlation_id=correlation_id,
            request_duration_ms=duration_ms,
            additional_context={"endpoint": "/mcp/server/protocol", "auth_provided": bool(authorization)}
        )
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": "Authentication required"}
            },
            status_code=401
        )
    
    try:
        # Parse request body with timing
        parse_start = time.time()
        body = await request.json()
        parse_duration = (time.time() - parse_start) * 1000
        method = body.get('method')
        request_id = body.get('id')
        
        logger.info(f"MCP POST /protocol - Processing request: method={method}, id={request_id}, correlation_id={correlation_id}, parse_duration={parse_duration:.2f}ms")
        
        # Process with timeout protection
        process_start = time.time()
        handler = MCPProtocolHandler(user)
        
        # Add timeout for tool calls (30 seconds)
        timeout_seconds = 30.0
        try:
            response = await asyncio.wait_for(
                handler.handle_message(body),
                timeout=timeout_seconds
            )
            process_duration = (time.time() - process_start) * 1000
            total_duration = (time.time() - start_time) * 1000
            
            # Log slow requests
            if total_duration > 5000:
                logger.warning(f"MCP POST /protocol - Slow request: method={method}, total_duration={total_duration:.2f}ms, process_duration={process_duration:.2f}ms, correlation_id={correlation_id}")
            
            # Log response summary
            result_preview = ""
            try:
                if response.get('result'):
                    if 'content' in response['result']:
                        content = response['result']['content']
                        if isinstance(content, list) and content:
                            first = content[0]
                            result_preview = (first.get('text', '')[:100] if isinstance(first, dict) else str(first)[:100])
                    elif 'tools' in response['result']:
                        result_preview = f"tools_list({len(response['result']['tools'])})"
                    else:
                        result_preview = str(response['result'])[:100]
            except Exception:
                result_preview = "preview_error"
            
            logger.info(f"MCP POST /protocol - Success: method={method}, duration={total_duration:.2f}ms, correlation_id={correlation_id}, result_preview={result_preview[:50]}")
            
            return JSONResponse(content=response)
            
        except asyncio.TimeoutError:
            process_duration = (time.time() - process_start) * 1000
            total_duration = (time.time() - start_time) * 1000
            timeout_error = TimeoutError(f"Request timeout after {timeout_seconds}s for method {method}")
            
            logger.error(f"MCP POST /protocol - Timeout: method={method}, process_duration={process_duration:.2f}ms, total_duration={total_duration:.2f}ms, correlation_id={correlation_id}")
            
            await log_error(
                request,
                timeout_error,
                user_id=user_id,
                correlation_id=correlation_id,
                request_duration_ms=total_duration,
                is_timeout=True,
                additional_context={
                    "method": method,
                    "request_id": request_id,
                    "process_duration_ms": process_duration,
                    "timeout_threshold_seconds": timeout_seconds,
                    "handler_type": "MCPProtocolHandler"
                }
            )
            
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": f"Request timeout after {timeout_seconds}s"}
                },
                status_code=504
            )
    
    except json.JSONDecodeError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"MCP POST /protocol - JSON decode error: {e}, correlation_id={correlation_id}, duration={duration_ms:.2f}ms")
        
        try:
            raw_body = await request.body()
            body_preview = raw_body[:500].decode('utf-8', errors='ignore') if raw_body else None
        except:
            body_preview = None
        
        await log_error(
            request,
            e,
            user_id=user_id,
            correlation_id=correlation_id,
            request_duration_ms=duration_ms,
            additional_context={
                "body_preview": body_preview,
                "body_length": len(raw_body) if 'raw_body' in locals() else 0
            }
        )
        
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            },
            status_code=400
        )
    except MCPAuthError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"MCP POST /protocol - Auth error: {e.detail}, correlation_id={correlation_id}, duration={duration_ms:.2f}ms")
        
        await log_error(
            request,
            e,
            user_id=user_id,
            correlation_id=correlation_id,
            request_duration_ms=duration_ms,
            additional_context={"auth_error": True, "status_code": e.status_code}
        )
        
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(e.detail)}
            },
            status_code=e.status_code
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"MCP POST /protocol - Unexpected error: {e}, correlation_id={correlation_id}, duration={duration_ms:.2f}ms", exc_info=True)
        
        await log_error(
            request,
            e,
            user_id=user_id,
            correlation_id=correlation_id,
            request_duration_ms=duration_ms,
            additional_context={
                "endpoint": "/mcp/server/protocol",
                "method": body.get('method') if 'body' in locals() else None,
                "request_id": body.get('id') if 'body' in locals() else None
            }
        )
        
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": body.get('id') if 'body' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            },
            status_code=500
        )


@router.api_route("/protocol/sse", methods=["GET", "POST"])
async def mcp_sse_endpoint(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    MCP Protocol SSE endpoint for streaming transport.
    Used by ChatGPT for real-time communication.
    
    Supports both GET and POST methods (ChatGPT tries POST first).
    Supports discovery without auth, but requires auth for actual operations.
    """
    logger.info(f"MCP GET /protocol/sse - Headers: {dict(request.headers)}")
    logger.info(f"MCP GET /protocol/sse - Authorization: {'Present' if authorization else 'Missing'}")
    
    user = None
    
    # Try to authenticate if authorization header is provided
    if authorization:
        try:
            user = await get_mcp_user(authorization, request)
            logger.info(f"MCP GET /protocol/sse - Authentication successful: user_id={user.user_id}")
        except MCPAuthError as e:
            logger.error(f"MCP GET /protocol/sse - Authentication failed: {e.detail}, status={e.status_code}")
            # Return error as SSE event
            async def error_stream():
                yield f"event: error\ndata: {json.dumps({'error': str(e.detail), 'code': e.status_code})}\n\n"
            return StreamingResponse(
                error_stream(),
                media_type="text/event-stream",
                status_code=e.status_code,
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
    else:
        # No auth provided - return server info as SSE event for discovery
        logger.info("MCP GET /protocol/sse - No auth provided, returning discovery info")
        async def discovery_stream():
            import asyncio
            base_url = settings.backend_url.rstrip('/')
            server_info = {
                "name": settings.mcp_server_name,
                "version": settings.mcp_server_version,
                "protocol_version": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                },
                "serverInfo": {
                    "name": settings.mcp_server_name,
                    "version": settings.mcp_server_version,
                },
                "authentication": {
                    "oauth2": True,
                    "api_key": True,
                },
                "oauth": {
                    "discovery_url": f"{base_url}/.well-known/oauth-authorization-server",
                    "authorization_endpoint": f"{base_url}/mcp/server/oauth/authorize",
                    "token_endpoint": f"{base_url}/mcp/server/oauth/token",
                    "registration_endpoint": f"{base_url}/mcp/server/oauth/register",
                },
                "endpoints": {
                    "protocol": f"{base_url}/mcp/server/protocol",
                    "sse": f"{base_url}/mcp/server/protocol/sse",
                    "oauth_authorize": f"{base_url}/mcp/server/oauth/authorize",
                    "oauth_token": f"{base_url}/mcp/server/oauth/token",
                },
                "message": "OAuth2 authentication required. Use the oauth.discovery_url to configure OAuth."
            }
            yield f"event: server_info\ndata: {json.dumps(server_info)}\n\n"
            await asyncio.sleep(0.1)
            # Don't send error - just info about using POST endpoint
            yield f"event: info\ndata: {json.dumps({'message': 'For JSON-RPC requests, use POST /mcp/server/protocol endpoint'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Keep connection alive briefly for ChatGPT to read
            await asyncio.sleep(2)
        
        return StreamingResponse(
            discovery_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    async def event_stream():
        """Generate SSE events"""
        import asyncio
        
        logger.info(f"MCP GET /protocol/sse - Starting SSE stream for user {user.user_id}")
        
        # Send initial connection event immediately
        yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'user_id': user.user_id})}\n\n"
        await asyncio.sleep(0.1)  # Small delay to ensure message is sent
        
        # Send server capabilities
        yield f"event: capabilities\ndata: {json.dumps({'tools': True, 'resources': False, 'prompts': False})}\n\n"
        await asyncio.sleep(0.1)
        
        logger.info("MCP GET /protocol/sse - SSE stream established, starting keepalive")
        
        # Keep connection alive with periodic pings
        ping_interval = 15  # Ping every 15 seconds
        ping_count = 0
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info(f"MCP GET /protocol/sse - Client disconnected after {ping_count} pings")
                break
            
            # Wait and send ping
            await asyncio.sleep(ping_interval)
            
            # Check again after sleep
            if await request.is_disconnected():
                logger.info(f"MCP GET /protocol/sse - Client disconnected during ping wait")
                break
            
            ping_count += 1
            logger.debug(f"MCP GET /protocol/sse - Sending ping #{ping_count}")
            yield f"event: ping\ndata: {json.dumps({'type': 'ping', 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ==================== OAuth2 Endpoints ====================

# Allowed OAuth redirect URIs for ChatGPT, Claude, and local dev
ALLOWED_REDIRECT_URIS = [
    "https://chatgpt.com/connector_platform_oauth_redirect",
    "https://platform.openai.com/apps-manage/oauth",
    "https://claude.ai/oauth/callback",        # Claude connector
    "https://claude.ai/api/mcp/auth_callback", # Claude MCP connector
    "https://aiveilix.com/oauth/callback",     # Production frontend
    "https://www.aiveilix.com/oauth/callback",  # Production frontend (www)
    "https://aiveilix-427f3.web.app/oauth/callback",  # Firebase hosting
    "https://aiveilix-427f3.firebaseapp.com/oauth/callback",  # Firebase hosting
    "http://localhost:6677/oauth/callback",     # Frontend callback
    "http://localhost:7223/oauth/callback",     # Backend callback (if needed)
    "http://127.0.0.1:6677/oauth/callback",    # Frontend callback
    "http://127.0.0.1:7223/oauth/callback",    # Backend callback (if needed)
]


@router.api_route("/oauth/authorize", methods=["GET", "POST"])
async def oauth_authorize(
    request: Request,
    response_type: Optional[str] = None,
    client_id: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    scope: Optional[str] = "read:buckets read:files query chat",
    state: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = "S256",
    resource: Optional[str] = None,
):
    """
    OAuth2 authorization endpoint with PKCE support.
    Redirects to React frontend for user login and consent.
    """
    # Handle both GET and POST
    if request.method == "POST":
        form_data = await request.form()
        response_type = response_type or form_data.get("response_type")
        client_id = client_id or form_data.get("client_id")
        redirect_uri = redirect_uri or form_data.get("redirect_uri")
        scope = scope or form_data.get("scope", "read:buckets read:files query chat")
        state = state or form_data.get("state")
        code_challenge = code_challenge or form_data.get("code_challenge")
        code_challenge_method = code_challenge_method or form_data.get("code_challenge_method", "S256")
        resource = resource or form_data.get("resource")

    # Validate required parameters
    if not response_type:
        raise HTTPException(status_code=400, detail="response_type is required")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required")
    if not redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri is required")

    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only response_type=code is supported")

    logger.info(f"OAuth authorize request: client_id={client_id}, redirect_uri={redirect_uri}, PKCE={bool(code_challenge)}")

    oauth_service = get_oauth2_service()

    # Validate client exists (don't check redirect_uri match yet - allow ChatGPT URIs)
    client = await oauth_service.get_client(client_id)
    if not client:
        logger.warning(f"Invalid client: client_id={client_id}")
        raise HTTPException(status_code=400, detail="Invalid client_id")

    # Allow redirect_uri if:
    # 1. Matches client's registered URI, OR
    # 2. Is in the hardcoded allowlist, OR
    # 3. Client was registered via DCR (no user_id) - trust their redirect_uri
    is_dcr_client = not client.get("user_id")
    if redirect_uri != client["redirect_uri"] and redirect_uri not in ALLOWED_REDIRECT_URIS and not is_dcr_client:
        logger.warning(f"Redirect URI not allowed: {redirect_uri}, registered: {client['redirect_uri']}")
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    logger.info(f"OAuth redirect_uri accepted: {redirect_uri} (registered: {client['redirect_uri']}, dcr: {is_dcr_client})")

    # P2 Fix: Guard against missing/empty frontend_url
    if not settings.frontend_url:
        logger.error("OAuth authorize: settings.frontend_url is not configured")
        raise HTTPException(status_code=500, detail="Server misconfiguration: frontend URL not set")

    # Redirect to React frontend for login + consent
    # The frontend will handle authentication and call back to /oauth/approve
    from urllib.parse import urlencode, quote
    frontend_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope or "read:buckets read:files query chat",
        "response_type": response_type,
    }
    if state:
        frontend_params["state"] = state
    if code_challenge:
        frontend_params["code_challenge"] = code_challenge
    if code_challenge_method:
        frontend_params["code_challenge_method"] = code_challenge_method
    if resource:
        frontend_params["resource"] = resource

    frontend_url = f"{settings.frontend_url}/oauth/authorize?{urlencode(frontend_params)}"
    logger.info(f"Redirecting to React frontend for login: {frontend_url}")

    return RedirectResponse(url=frontend_url, status_code=302)


@router.post("/oauth/approve")
async def oauth_approve(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(...),
    state: Optional[str] = Form(None),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form(None),
    resource: Optional[str] = Form(None),
    access_token: str = Form(..., description="User's Supabase JWT token"),
):
    """
    OAuth2 approval endpoint - called by React frontend after user logs in and consents.
    Creates authorization code and redirects back to the OAuth client (ChatGPT/Claude).
    """
    logger.info(f"OAuth approve: client_id={client_id}, redirect_uri={redirect_uri}")

    # Verify the user's JWT token to get user_id
    from app.services.supabase import get_supabase_auth
    try:
        supabase_auth = get_supabase_auth()
        user_response = supabase_auth.auth.get_user(access_token)
        user_id = str(user_response.user.id)
        logger.info(f"OAuth approve: verified user_id={user_id}")
    except Exception as e:
        logger.error(f"OAuth approve: invalid token - {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired user token")

    oauth_service = get_oauth2_service()

    # Validate client
    client = await oauth_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client_id")

    # Check if client was registered via DCR (no user_id)
    is_dcr_client = not client.get("user_id")
    logger.info(f"OAuth approve: client user_id={client.get('user_id')!r}, is_dcr={is_dcr_client}, scopes={client.get('scopes')}")

    # Validate redirect_uri against client's registered URI, allowlist, or DCR client
    if redirect_uri != client["redirect_uri"] and redirect_uri not in ALLOWED_REDIRECT_URIS and not is_dcr_client:
        logger.warning(f"OAuth approve: redirect_uri not allowed: {redirect_uri}")
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    # Enforce requested scopes - DCR clients get all standard scopes automatically
    requested_scopes = set(scope.split())
    allowed_scopes = set(client.get("scopes") or [])
    # Always allow standard MCP scopes for any client
    allowed_scopes.update(["read:buckets", "read:files", "query", "chat", "offline_access"])
    if not requested_scopes.issubset(allowed_scopes):
        disallowed = requested_scopes - allowed_scopes
        logger.warning(f"OAuth approve: scopes not allowed: {disallowed}, requested={requested_scopes}, allowed={allowed_scopes}")
        raise HTTPException(
            status_code=400,
            detail=f"Requested scopes not allowed: {', '.join(disallowed)}"
        )

    # Create authorization code
    try:
        auth_code = await oauth_service.create_authorization_code(
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method if code_challenge else None,
            resource=resource,
        )

        logger.info(f"OAuth authorization code created: client_id={client_id}, user_id={user_id}")

        # Redirect back to the OAuth client with the code
        from urllib.parse import urlencode
        redirect_params = {"code": auth_code}
        if state:
            redirect_params["state"] = state

        redirect_url = f"{redirect_uri}?{urlencode(redirect_params)}"
        return RedirectResponse(url=redirect_url, status_code=302)

    except Exception as e:
        logger.error(f"Error creating authorization code: {e}", exc_info=True)
        from urllib.parse import urlencode
        error_params = {
            "error": "server_error",
            "error_description": "Failed to create authorization code",
        }
        if state:
            error_params["state"] = state
        return RedirectResponse(url=f"{redirect_uri}?{urlencode(error_params)}", status_code=302)


@router.post("/oauth/token")
async def oauth_token(
    http_request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    resource: Optional[str] = Form(None),
):
    """
    OAuth2 token endpoint with PKCE support.
    Exchanges authorization code for access token, or refreshes tokens.
    Accepts application/x-www-form-urlencoded (OAuth2 standard).

    client_secret is optional for PKCE public clients (they use code_verifier instead).
    """
    logger.info(f"OAuth token request: grant_type={grant_type}, client_id={client_id}, has_secret={bool(client_secret)}, has_verifier={bool(code_verifier)}")

    oauth_service = get_oauth2_service()

    if grant_type == "authorization_code":
        if not code or not redirect_uri:
            raise HTTPException(
                status_code=400,
                detail="code and redirect_uri required for authorization_code grant"
            )

        # For PKCE public clients: client_secret is optional if code_verifier is provided
        if client_secret:
            valid, client = await oauth_service.validate_client(client_id, client_secret)
            if not valid:
                logger.warning(f"Invalid client credentials: client_id={client_id}")
                raise HTTPException(status_code=401, detail="Invalid client credentials")
        else:
            # Public client - just verify client exists
            client = await oauth_service.get_client(client_id)
            if not client:
                logger.warning(f"Unknown client_id: {client_id}")
                raise HTTPException(status_code=401, detail="Invalid client_id")
            # PKCE is required for public clients
            if not code_verifier:
                raise HTTPException(
                    status_code=400,
                    detail="code_verifier is required for public clients (no client_secret)"
                )

        # Validate authorization code with PKCE verification
        code_data = await oauth_service.validate_authorization_code(
            code,
            client_id,
            redirect_uri,
            code_verifier=code_verifier
        )
        if not code_data:
            logger.warning(f"Invalid or expired authorization code: client_id={client_id}")
            raise HTTPException(status_code=400, detail="Invalid or expired authorization code")

        # Get resource from code data or request
        final_resource = code_data.get("resource") or resource

        # Determine audience (MCP server URL)
        base_url = settings.backend_url.rstrip('/')
        audience = f"{base_url}/mcp/server"

        # Create tokens with resource and audience
        tokens = await oauth_service.create_tokens(
            client_id=client_id,
            user_id=code_data["user_id"],
            scope=code_data["scope"],
            resource=final_resource,
            audience=audience
        )

        logger.info(f"OAuth tokens created: client_id={client_id}, user_id={code_data['user_id']}")
        return tokens.dict()

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(
                status_code=400,
                detail="refresh_token required for refresh_token grant"
            )

        # For refresh, client_secret may or may not be present
        if client_secret:
            tokens = await oauth_service.refresh_tokens(
                refresh_token,
                client_id,
                client_secret
            )
        else:
            # Public client refresh - validate client exists and refresh token matches
            tokens = await oauth_service.refresh_tokens_public(
                refresh_token,
                client_id
            )

        if not tokens:
            logger.warning(f"Invalid or expired refresh token: client_id={client_id}")
            raise HTTPException(status_code=400, detail="Invalid or expired refresh token")

        logger.info(f"OAuth tokens refreshed: client_id={client_id}")
        return tokens.dict()

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported grant_type: {grant_type}"
        )


@router.post("/oauth/register")
async def oauth_register(
    request: OAuthClientCreate,
    http_request: Request,
):
    """
    Dynamic Client Registration (RFC 7591).
    Creates a new OAuth client. No authentication required - ChatGPT/Claude
    call this endpoint before any auth exists to register themselves as clients.

    The client is created without a user_id initially. The user association
    happens during the authorization flow when the user logs in and consents.
    """
    logger.info(f"OAuth DCR request (public): name={request.name}, redirect_uri={request.redirect_uri}")

    oauth_service = get_oauth2_service()

    try:
        client = await oauth_service.create_client_public(
            client_data=request
        )

        logger.info(f"OAuth client registered (public): client_id={client.client_id}")

        # Return client registration response (RFC 7591 format)
        base_url = settings.backend_url.rstrip('/')
        return {
            "client_id": client.client_id,
            "client_secret": client.client_secret,  # Only shown once!
            "client_id_issued_at": int(client.created_at.timestamp()),
            "client_secret_expires_at": 0,  # 0 means never expires
            "redirect_uris": [client.redirect_uri],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "client_name": client.name,
            "scope": " ".join(client.scopes),
            "token_endpoint_auth_method": "none",
            "application_type": "web"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OAuth DCR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to register OAuth client")


@router.post("/oauth/revoke")
async def oauth_revoke(
    token: str,
    user: MCPUser = Depends(get_mcp_user)
):
    """Revoke an OAuth token"""
    oauth_service = get_oauth2_service()
    success = await oauth_service.revoke_token(token)
    return {"revoked": success}


# ==================== Resource HTTP Endpoints ====================

@router.get("/resources")
async def list_resources(user: MCPUser = Depends(get_mcp_user)):
    """
    List all available MCP resources.
    Used by Cursor and other MCP clients that support resources.
    """
    handler = MCPProtocolHandler(user)
    result = await handler.handle_resources_list()
    return result


@router.get("/resources/read")
async def read_resource(
    uri: str,
    user: MCPUser = Depends(get_mcp_user)
):
    """
    Read a specific MCP resource by URI.
    
    Example URIs:
    - aiveilix://buckets
    - aiveilix://buckets/{id}
    - aiveilix://buckets/{id}/files
    - aiveilix://buckets/{id}/search?q=query
    """
    handler = MCPProtocolHandler(user)
    try:
        result = await handler.handle_resources_read({"uri": uri})
        return result
    except MCPServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


# ==================== Server Info Endpoints ====================

@router.get("/info")
async def mcp_server_info():
    """Get MCP server information"""
    return {
        "name": settings.mcp_server_name,
        "version": settings.mcp_server_version,
        "protocol_version": "2024-11-05",
        "capabilities": {
            "tools": True,
            "resources": True,  # Now enabled!
            "prompts": False,
        },
        "authentication": {
            "oauth2": True,
            "api_key": True,
        },
        "endpoints": {
            "protocol": "/mcp/server/protocol",
            "sse": "/mcp/server/protocol/sse",
            "resources": "/mcp/server/resources",
            "resources_read": "/mcp/server/resources/read?uri=",
            "oauth_authorize": "/mcp/server/oauth/authorize",
            "oauth_token": "/mcp/server/oauth/token",
        },
        "resource_uris": {
            "buckets_list": "aiveilix://buckets",
            "bucket_info": "aiveilix://buckets/{bucket_id}",
            "bucket_files": "aiveilix://buckets/{bucket_id}/files",
            "bucket_search": "aiveilix://buckets/{bucket_id}/search?q={query}",
        }
    }


@router.get("/tools")
async def list_mcp_tools():
    """List available MCP tools (public endpoint for discovery)"""
    return {"tools": MCP_TOOLS}
