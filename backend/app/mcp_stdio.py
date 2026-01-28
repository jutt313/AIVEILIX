#!/usr/bin/env python3
"""
MCP Stdio Transport Entry Point for AIveilix using Official MCP SDK

Run this script to start the MCP server over stdio transport.
Used by Cursor and other local MCP clients.

Usage:
    python -m app.mcp_stdio --api-key <your-api-key>
    or set AIVEILIX_API_KEY environment variable
"""
import sys
import os
import asyncio
import logging
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

from app.config import get_settings
from app.services.mcp_auth import _authenticate_api_key
from app.services.mcp_services import (
    list_buckets_service,
    list_files_service,
    query_bucket_service,
    chat_bucket_service,
    get_bucket_info_service,
)
from app.models.oauth import MCPUser

settings = get_settings()

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
    force=True
)
logger = logging.getLogger(__name__)

# Disable httpx logging to prevent exposing Supabase URLs in Cursor logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def sanitize_error(error: Exception) -> str:
    """Remove sensitive info from errors before logging"""
    msg = str(error)
    # Remove DB URLs with passwords
    msg = re.sub(r'postgresql://[^:]+:[^@]+@[^/]+', 'postgresql://[REDACTED]', msg)
    # Remove API keys
    msg = re.sub(r'(sk-|AIza)[a-zA-Z0-9_-]{20,}', '[REDACTED]', msg)
    return msg

# Global user (authenticated on startup)
mcp_user: MCPUser = None

# Create MCP server
app = Server("aiveilix-mcp")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available MCP resources"""
    if not mcp_user:
        return []
    
    try:
        buckets = await list_buckets_service(mcp_user)
        resources = []
        
        # Root buckets list
        resources.append(Resource(
            uri="aiveilix://buckets",
            name="All Buckets",
            description=f"List of all {len(buckets)} knowledge buckets",
            mimeType="application/json"
        ))
        
        # Each bucket
        for bucket in buckets:
            resources.append(Resource(
                uri=f"aiveilix://buckets/{bucket.id}",
                name=bucket.name,
                description=bucket.description or f"Bucket with {bucket.file_count} files",
                mimeType="text/markdown"
            ))
            
            resources.append(Resource(
                uri=f"aiveilix://buckets/{bucket.id}/files",
                name=f"{bucket.name} - Files",
                description=f"Files in {bucket.name}",
                mimeType="text/markdown"
            ))
        
        return resources
    except Exception as e:
        logger.error(f"Error listing resources: {sanitize_error(e)}")
        return []


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource"""
    if not mcp_user:
        return "Not authenticated"
    
    try:
        # aiveilix://buckets
        if uri == "aiveilix://buckets":
            buckets = await list_buckets_service(mcp_user)
            content = "# Your Knowledge Buckets\n\n"
            for bucket in buckets:
                content += f"## {bucket.name}\n"
                content += f"- **ID**: `{bucket.id}`\n"
                content += f"- **Description**: {bucket.description or 'No description'}\n"
                content += f"- **Files**: {bucket.file_count}\n"
                content += f"- **Size**: {bucket.total_size_bytes:,} bytes\n\n"
            return content if buckets else "No buckets found."
        
        # aiveilix://buckets/{id}
        if uri.startswith("aiveilix://buckets/") and uri.count("/") == 3:
            bucket_id = uri.split("/")[-1]
            info = await get_bucket_info_service(bucket_id, mcp_user)
            files = await list_files_service(bucket_id, mcp_user)
            
            content = f"# {info['name']}\n\n"
            content += f"**Description**: {info['description'] or 'No description'}\n\n"
            content += f"**Total Files**: {info['file_count']}\n\n"
            content += "## Files\n\n"
            for f in files[:50]:
                status_icon = "✅" if f.status == "ready" else "⏳"
                content += f"- {status_icon} **{f.name}** ({f.size_bytes:,} bytes)\n"
            return content
        
        # aiveilix://buckets/{id}/files
        if uri.endswith("/files"):
            bucket_id = uri.split("/")[-2]
            files = await list_files_service(bucket_id, mcp_user)
            
            content = "# Files\n\n"
            for f in files:
                content += f"- **{f.name}** - {f.status} - {f.size_bytes:,} bytes\n"
            return content if files else "No files found."
        
        return "Resource not found"
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {sanitize_error(e)}")
        return "Error reading resource"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="list_buckets",
            description="List all knowledge buckets accessible to the user",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="query_bucket",
            description="Search bucket content using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_id": {"type": "string", "description": "Bucket UUID"},
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["bucket_id", "query"]
            }
        ),
        Tool(
            name="chat_bucket",
            description="Chat with a bucket using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_id": {"type": "string", "description": "Bucket UUID"},
                    "message": {"type": "string", "description": "Your message"}
                },
                "required": ["bucket_id", "message"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool"""
    if not mcp_user:
        return [TextContent(type="text", text="Not authenticated")]
    
    try:
        if name == "list_buckets":
            buckets = await list_buckets_service(mcp_user)
            text = f"Found {len(buckets)} buckets:\n\n"
            for b in buckets:
                text += f"- **{b.name}** (ID: {b.id}) - {b.file_count} files\n"
            return [TextContent(type="text", text=text)]
        
        elif name == "query_bucket":
            result = await query_bucket_service(
                arguments["bucket_id"],
                arguments["query"],
                mcp_user,
                arguments.get("max_results", 10)
            )
            text = f"Query: \"{result['query']}\"\nFound {result['total']} results:\n\n"
            for i, r in enumerate(result['results'][:5], 1):
                text += f"**{i}. {r.file_name}** (relevance: {r.relevance_score:.2f})\n{r.content[:200]}...\n\n"
            return [TextContent(type="text", text=text)]
        
        elif name == "chat_bucket":
            result = await chat_bucket_service(
                arguments["bucket_id"],
                arguments["message"],
                mcp_user,
                arguments.get("conversation_id")
            )
            return [TextContent(type="text", text=result['response'])]
        
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool error: {sanitize_error(e)}")
        return [TextContent(type="text", text="An error occurred")]


async def main():
    """Main entry point"""
    global mcp_user
    
    # Get API key from environment
    api_key = os.environ.get("AIVEILIX_API_KEY")
    if not api_key:
        logger.error("AIVEILIX_API_KEY environment variable not set")
        sys.exit(1)
    
    # Authenticate
    logger.info("Authenticating...")
    mcp_user = await _authenticate_api_key(api_key)
    if not mcp_user:
        logger.error("Authentication failed")
        sys.exit(1)
    
    logger.info(f"Authenticated as user {mcp_user.user_id}")
    logger.info("Starting MCP stdio server...")
    
    # Run the stdio server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
