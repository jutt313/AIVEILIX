# Integrations (MCP) - AIveilix

Complete guide to integrating AIveilix with your favorite tools using the Model Context Protocol (MCP).

---

## Table of Contents

1. [Overview](#overview)
2. [Cursor Setup](#cursor-setup)
3. [Claude Desktop Setup](#claude-desktop-setup)
4. [ChatGPT Setup](#chatgpt-setup)
5. [Zed Editor Setup](#zed-editor-setup)
6. [Continue.dev (VS Code) Setup](#continuedev-vs-code-setup)
7. [Custom Python Client](#custom-python-client)
8. [Custom Node.js Client](#custom-nodejs-client)
9. [Postman & cURL Testing](#postman--curl-testing)
10. [Generic MCP Client](#generic-mcp-client)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### What is MCP?

**Model Context Protocol (MCP)** is an open standard created by Anthropic for connecting AI applications to external data sources. Think of it as **"USB for AI tools"** - one protocol, universal compatibility.


**Why MCP?**

**Before MCP:**
```
You → Upload file to Claude
You → Upload SAME file to ChatGPT
You → Upload SAME file to Cursor
You → Upload SAME file to every AI tool

= Wasted time, duplicated data, no sync
```

**After MCP:**
```
You → Upload ONCE to AIveilix
Claude ←──┐
ChatGPT ←─┤ MCP Protocol → AIveilix
Cursor ←──┤
Zed ←─────┘

= Single source of truth, instant access everywhere
```

### MCP Architecture

```
┌─────────────────────────────────────────────┐
│         AI Application (Client)             │
│    (Cursor, Claude, ChatGPT, VS Code)       │
└────────────────┬────────────────────────────┘
                 │
                 │ MCP Protocol
                 │ (stdio or HTTP)
                 │
┌────────────────▼────────────────────────────┐
│         AIveilix MCP Server                 │
│   - Resources (buckets, files)              │
│   - Tools (list, query, chat)               │
│   - Authentication (API keys/OAuth)         │
└────────────────┬────────────────────────────┘
                 │
                 │ Secure API
                 │
┌────────────────▼────────────────────────────┐
│      Your Knowledge Vault (Database)        │
│   - Files, Embeddings, Conversations        │
└─────────────────────────────────────────────┘
```

### Two MCP Implementations

AIveilix provides **two ways** to connect via MCP:

#### 1. MCP Stdio Transport (for Desktop Apps)


**How it works:**
- AI app launches Python process: `python -m app.mcp_stdio`
- Communication via stdin/stdout (standard input/output)
- Process stays alive while app is open
- Best for: Cursor, Claude Desktop, Zed

**Authentication:**
- Environment variable: `AIVEILIX_API_KEY=aiveilix_sk_live_...`
- Passed when launching process
- Validated on startup

**Example Launch:**
```bash
AIVEILIX_API_KEY=aiveilix_sk_live_abc123... python -m app.mcp_stdio
```

#### 2. MCP HTTP Transport (for Web Apps & Custom Clients)


**How it works:**
- RESTful API endpoints
- Standard HTTP requests
- CORS enabled for web apps
- Best for: ChatGPT, custom clients, Postman

**Base URL:**
```
Development: http://localhost:7223
Production: https://api.aiveilix.com
```

**Authentication:**
- HTTP Header: `Authorization: Bearer aiveilix_sk_live_...`
- Or OAuth2 access token
- Validated on every request

**Endpoints:**
```
GET  /mcp/buckets                      - List accessible buckets
GET  /mcp/buckets/{id}/files           - List files in bucket
POST /mcp/buckets/{id}/query           - Semantic search
POST /mcp/buckets/{id}/chat            - Chat with bucket
```

### Creating Your API Key



**Step-by-Step:**

1. **Login to AIveilix** at https://aiveilix.com

2. **Open Profile Settings:**
   - Click **Profile icon** (top-right)
   - Click **"Credentials"** tab

3. **Create API Key:**
   - Click **"Create Credential"** button
   - Select **"API Key"** type


4. **Configure Key:**

**Name:**
```
Example: "Cursor Integration"
Example: "Claude Desktop"
Example: "My Custom App"
```

**Scopes (Permissions):**
- ☑️ **read** - View files and buckets
- ☑️ **write** - Upload files
- ☑️ **delete** - Remove files
- ☑️ **query** - Semantic search
- ☑️ **chat** - AI chat features
- ☑️ **full** - All permissions (recommended for personal use)

**Allowed Buckets:**
- **All Buckets** - Access to all your buckets (recommended)
- **Specific Buckets** - Select individual buckets (for sharing/team use)


5. **Create & Copy Key:**

Click **"Create"** button

**ONE-TIME DISPLAY:**
```
┌─────────────────────────────────────────────┐
│  API Key Created Successfully               │
│                                             │
│  Please copy your API key now. You won't    │
│  be able to see it again!                   │
│                                             │
│  aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0...  │
│                                             │
│  [Copy]                                     │
│                                             │
│  [I've Saved My Key]                        │
└─────────────────────────────────────────────┘
```


**CRITICAL:**
- ⚠️ Copy key immediately
- ⚠️ Store in password manager (1Password, LastPass, etc.)
- ⚠️ Cannot view again after closing
- ⚠️ Only prefix shown in list: `aiveilix_sk_live_abc123...`

6. **Key Format:**
```
aiveilix_sk_live_[32-byte-random-token]

Example:
aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
│        │  │    │
│        │  │    └─ Random token (256 bits entropy)
│        │  └────── Environment (live/test)
│        └─────────Secret key
└──────────────────Platform identifier
```

**Security:**
- SHA-256 hashed before storage
- Only hash stored in database
- Prefix stored for display
- Full key never retrievable

### API Key Management

**Viewing Keys:**


Each key shows:
```
┌────────────────────────────────────────┐
│ Cursor Integration        [Active]     │
│ aiveilix_sk_live_abc123...             │
│ Last used: 2 hours ago • Requests: 145 │
│                            [Delete]    │
└────────────────────────────────────────┘
```

**Revoking Keys:**
1. Click **"Delete"** button
2. Confirm deletion
3. Key immediately invalidated
4. All apps using key will fail authentication

**Best Practices:**
- ✅ One key per application/device
- ✅ Descriptive names ("MacBook Cursor", "Work Desktop Claude")
- ✅ Rotate keys every 90 days
- ✅ Revoke unused keys
- ✅ Monitor request counts for unusual activity
- ❌ Never commit keys to git
- ❌ Never share keys publicly
- ❌ Don't use same key everywhere

---

## Cursor Setup

**Cursor** is an AI-powered code editor built on VS Code. With MCP, Cursor can read your AIveilix documents while you code.


### Prerequisites

- ✅ Cursor installed (https://cursor.sh)
- ✅ AIveilix account at `https://aiveilix.com`
- ✅ Python 3.10+ installed
- ✅ AIveilix API key created

### Step 1: Install AIveilix MCP Server

**Option A: From Source (Recommended for Development)**

```bash
# Navigate to AIveilix backend directory
cd /path/to/AIveilix/backend

# Ensure dependencies installed
pip install -r requirements.txt

# Test MCP server
AIVEILIX_API_KEY=your_key_here python -m app.mcp_stdio
```

**Option B: Pip Install (If Published)**

```bash
pip install aiveilix-mcp-server
```

### Step 2: Configure Cursor

**Location:** Cursor stores MCP configs in:

**macOS:**
```
~/Library/Application Support/Cursor/User/mcp_settings.json
```

**Windows:**
```
%APPDATA%\Cursor\User\mcp_settings.json
```

**Linux:**
```
~/.config/Cursor/User/mcp_settings.json
```


### Step 3: Add AIveilix MCP Configuration

**Open Cursor Settings:**

1. Open Cursor
2. Press **Cmd+Shift+P** (Mac) or **Ctrl+Shift+P** (Windows/Linux)
3. Type: **"Preferences: Open MCP Settings"**
4. Press Enter

**Or manually create/edit:** `mcp_settings.json`


### Step 4: Add Configuration

**Full Configuration:**

```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python",
      "args": ["-m", "app.mcp_stdio"],
      "env": {
        "AIVEILIX_API_KEY": "aiveilix_sk_live_YOUR_KEY_HERE",
        "PYTHONPATH": "/absolute/path/to/AIveilix/backend"
      },
      "cwd": "/absolute/path/to/AIveilix/backend"
    }
  }
}
```

**Configuration Breakdown:**

| Field | Value | Description |
|-------|-------|-------------|
| `mcpServers` | Object | Container for all MCP server configs |
| `"aiveilix"` | Key | Identifier for this server (can be any name) |
| `command` | `"python"` | Command to launch (Python interpreter) |
| `args` | `["-m", "app.mcp_stdio"]` | Module to run (MCP stdio server) |
| `env.AIVEILIX_API_KEY` | Your API key | Authentication credential |
| `env.PYTHONPATH` | Backend path | Python module search path |
| `cwd` | Backend directory | Working directory for process |

**Example with Real Paths (macOS):**

```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python3",
      "args": ["-m", "app.mcp_stdio"],
      "env": {
        "AIVEILIX_API_KEY": "aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "PYTHONPATH": "/Users/yourusername/Projects/AIveilix/backend"
      },
      "cwd": "/Users/yourusername/Projects/AIveilix/backend"
    }
  }
}
```

**Example with Real Paths (Windows):**

```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python",
      "args": ["-m", "app.mcp_stdio"],
      "env": {
        "AIVEILIX_API_KEY": "aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "PYTHONPATH": "C:\\Users\\YourName\\Projects\\AIveilix\\backend"
      },
      "cwd": "C:\\Users\\YourName\\Projects\\AIveilix\\backend"
    }
  }
}
```

### Step 5: Restart Cursor

1. Close Cursor completely
2. Reopen Cursor
3. MCP server launches automatically


### Step 6: Verify Connection

**Check MCP Status:**

1. Open Cursor
2. Press **Cmd+Shift+P** / **Ctrl+Shift+P**
3. Type: **"MCP: Show MCP Servers"**
4. Should see **"aiveilix"** with **green checkmark** ✅


**Alternative Check - Logs:**

```bash
# View Cursor logs
# macOS/Linux:
tail -f ~/Library/Logs/Cursor/main.log

# Windows:
Get-Content $env:APPDATA\Cursor\logs\main.log -Wait -Tail 50
```

Look for:
```
[MCP] Connected to aiveilix
[MCP] Resources available: 3 buckets
```

### Step 7: Use AIveilix in Cursor

**Access Your Documents:**


**Method 1: Chat Panel**

1. Open Chat (Cmd+L / Ctrl+L)
2. Type: `@aiveilix`
3. Autocomplete shows AIveilix resources
4. Select bucket or file
5. Ask questions

**Example:**
```
@aiveilix/Work Projects search "authentication flow"
```

**Method 2: Inline Context**

```python
# You're writing code:
def authenticate_user(email, password):
    # Type: Cmd+K (Mac) or Ctrl+K (Windows)
    # Ask: "How should I implement JWT auth based on @aiveilix/Architecture Docs?"
    pass
```

**Method 3: MCP Tools**

```
Tools available:
- aiveilix_list_buckets() - List all your buckets
- aiveilix_list_files(bucket_id) - List files in bucket
- aiveilix_query(bucket_id, query) - Semantic search
- aiveilix_chat(bucket_id, message) - AI chat
```


### Available Resources

**Resources Format:**
```
aiveilix://buckets/{bucket_id}
aiveilix://buckets/{bucket_id}/files
aiveilix://buckets/{bucket_id}/files/{file_id}
```

**Example:**
```
aiveilix://buckets/550e8400-e29b-41d4-a716-446655440000
aiveilix://buckets/550e8400-e29b-41d4-a716-446655440000/files
aiveilix://buckets/550e8400-e29b-41d4-a716-446655440000/files/abc123...
```

### MCP Tools Reference

**Tool:** `aiveilix_list_buckets`

**Description:** List all accessible buckets

**Parameters:** None

**Returns:**
```json
{
  "buckets": [
    {
      "id": "uuid",
      "name": "Work Projects",
      "description": "All work documents",
      "file_count": 45,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

**Usage in Cursor:**
```
"Show me my buckets"
```

---

**Tool:** `aiveilix_list_files`

**Description:** List files in a bucket

**Parameters:**
- `bucket_id` (string, required) - Bucket UUID

**Returns:**
```json
{
  "files": [
    {
      "id": "uuid",
      "name": "architecture.pdf",
      "size_bytes": 2048000,
      "status": "ready",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Usage in Cursor:**
```
"List files in Work Projects bucket"
```

---

**Tool:** `aiveilix_query`

**Description:** Semantic search in bucket

**Parameters:**
- `bucket_id` (string, required) - Bucket UUID
- `query` (string, required) - Search query
- `limit` (integer, optional) - Max results (default: 5)

**Returns:**
```json
{
  "results": [
    {
      "file_id": "uuid",
      "file_name": "auth.py",
      "content": "def authenticate_user(email, password):\n    ...",
      "similarity": 0.89,
      "chunk_index": 5
    }
  ]
}
```

**Usage in Cursor:**
```
"Search Work Projects for authentication code"
```

---

**Tool:** `aiveilix_chat`

**Description:** AI-powered chat with bucket contents

**Parameters:**
- `bucket_id` (string, required) - Bucket UUID
- `message` (string, required) - Your question
- `conversation_id` (string, optional) - Continue previous chat

**Returns:**
```json
{
  "message": "Based on your documents, the authentication flow uses JWT tokens...",
  "sources": [
    {
      "file_name": "architecture.pdf",
      "confidence": "high"
    }
  ],
  "conversation_id": "uuid"
}
```

**Usage in Cursor:**
```
"Ask Work Projects: How does authentication work?"
```

### Troubleshooting Cursor

**Issue:** "MCP server not found"

**Solution:**
```bash
# Check Python is in PATH
which python3  # macOS/Linux
where python   # Windows

# Verify PYTHONPATH is correct
cd /path/to/AIveilix/backend
python -m app.mcp_stdio
# Should show: MCP stdio server started
```

---

**Issue:** "Authentication failed"

**Solution:**
1. Verify API key is correct (check Profile → Credentials)
2. Check key is not revoked
3. Ensure `AIVEILIX_API_KEY` in config matches exact key
4. No extra spaces or quotes in key

---

**Issue:** "No buckets found"

**Solution:**
1. Create at least one bucket in AIveilix dashboard
2. Upload some files
3. Restart Cursor
4. Check API key has `read` scope

---

**Issue:** "Connection timeout"

**Solution:**
1. Verify AIveilix is accessible: `curl https://api.aiveilix.com`
2. Check your internet connection
3. Verify API key is valid and not expired
4. Check firewall/proxy settings

---

## Claude Desktop Setup

**Claude Desktop** by Anthropic supports MCP natively. Connect your AIveilix vault directly to Claude.


### Prerequisites

- ✅ Claude Desktop installed (https://claude.ai/download)
- ✅ AIveilix backend running
- ✅ Python 3.10+ installed
- ✅ AIveilix API key created

### Step 1: Locate Claude Config File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

**Create if doesn't exist:**
```bash
# macOS/Linux
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows (PowerShell)
New-Item -Path "$env:APPDATA\Claude" -ItemType Directory -Force
New-Item -Path "$env:APPDATA\Claude\claude_desktop_config.json" -ItemType File
```


### Step 2: Edit Configuration

**Open config file:**

```bash
# macOS/Linux
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or use any text editor
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Add AIveilix MCP Server:**

```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python",
      "args": ["-m", "app.mcp_stdio"],
      "env": {
        "AIVEILIX_API_KEY": "aiveilix_sk_live_YOUR_KEY_HERE",
        "PYTHONPATH": "/absolute/path/to/AIveilix/backend"
      },
      "cwd": "/absolute/path/to/AIveilix/backend"
    }
  }
}
```

**Example (macOS):**

```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python3",
      "args": ["-m", "app.mcp_stdio"],
      "env": {
        "AIVEILIX_API_KEY": "aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "PYTHONPATH": "/Users/john/Projects/AIveilix/backend"
      },
      "cwd": "/Users/john/Projects/AIveilix/backend"
    }
  }
}
```

**Example (Windows):**

```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python",
      "args": ["-m", "app.mcp_stdio"],
      "env": {
        "AIVEILIX_API_KEY": "aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "PYTHONPATH": "C:\\Users\\John\\Projects\\AIveilix\\backend"
      },
      "cwd": "C:\\Users\\John\\Projects\\AIveilix\\backend"
    }
  }
}
```

### Step 3: Multiple MCP Servers (Optional)

**You can add multiple servers:**

```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python",
      "args": ["-m", "app.mcp_stdio"],
      "env": {
        "AIVEILIX_API_KEY": "aiveilix_sk_live_...",
        "PYTHONPATH": "/path/to/AIveilix/backend"
      },
      "cwd": "/path/to/AIveilix/backend"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/john/Documents"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```


### Step 4: Restart Claude Desktop

1. **Quit Claude completely** (not just close window)
   - macOS: **Cmd+Q**
   - Windows: Right-click taskbar → Exit
2. **Reopen Claude Desktop**
3. MCP servers launch automatically

### Step 5: Verify Connection

**Check MCP Tools:**

1. Open Claude Desktop
2. Look for **tools icon** (hammer) in chat input
3. Click tools icon
4. Should see AIveilix tools:
   - `aiveilix_list_buckets`
   - `aiveilix_query`
   - `aiveilix_chat`


**Or check in conversation:**

```
You: "What MCP servers are connected?"

Claude: "I have access to the following MCP servers:
- aiveilix (for accessing your document vault)
  Tools: list_buckets, query, chat
  Status: Connected ✅
```

### Step 6: Use AIveilix in Claude

**Example Conversations:**


**List Your Buckets:**
```
You: "Show me my AIveilix buckets"

Claude: "I'll check your AIveilix buckets.
[Uses aiveilix_list_buckets tool]

You have 3 buckets:
1. Work Projects (45 files, 234 MB)
2. Personal Notes (12 files, 45 MB)
3. Research Papers (78 files, 567 MB)"
```

**Search Documents:**
```
You: "Search my Work Projects bucket for information about authentication"

Claude: [Uses aiveilix_query tool]
"I found several references to authentication in your Work Projects:

1. architecture.pdf (page 5):
'The system uses JWT tokens with 60-minute expiry...'

2. auth.py (line 23-45):
'def authenticate_user(email, password):
    # Validates credentials and generates token...'

Would you like me to explain the authentication flow?"
```

**Chat with Documents:**
```
You: "Ask my Work Projects: How does the payment processing work?"

Claude: [Uses aiveilix_chat tool]
"Based on your documents, the payment processing works as follows:

1. User initiates payment
2. Frontend sends request to /api/payments
3. Backend validates with Stripe API
4. Webhook confirms payment
5. Database updated

Sources: payment_flow.pdf, stripe_integration.py"
```

**Inline References:**
```
You: "I'm writing a new API endpoint. Can you check my Work Projects bucket for our existing API patterns?"

Claude: [Uses aiveilix_query and aiveilix_chat]
"I reviewed your existing APIs. Here's the standard pattern you're using:

[Provides code example based on your actual docs]

This matches the architecture described in your api_standards.md file."
```

### Advanced Claude Usage

**Combine with Claude's Capabilities:**

```
You: "Search my Research Papers for studies on neural networks,
     then write a 3-page summary with citations"

Claude:
[Uses aiveilix_query to find papers]
[Reads relevant sections]
[Writes summary with proper citations]
```

**Project-Specific Context:**

```
You: "I'm working on the authentication module.
     Keep my Work Projects/auth folder in context
     for this entire conversation"

Claude: "I'll maintain context from your auth folder.
[Uses aiveilix_list_files and aiveilix_query]

I see you have:
- auth.py (JWT implementation)
- auth_middleware.py (route protection)
- auth_tests.py (test suite)

How can I help with the authentication module?"
```

### Troubleshooting Claude

**Issue:** "Tools not appearing"

**Solution:**
```bash
# 1. Verify config file syntax (must be valid JSON)
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 2. Check for errors
cat ~/Library/Logs/Claude/mcp*.log

# 3. Verify API connectivity
curl https://api.aiveilix.com

# 4. Test MCP server manually
cd /path/to/AIveilix/backend
AIVEILIX_API_KEY=your_key python -m app.mcp_stdio
```

---

**Issue:** "Server keeps disconnecting"

**Solution:**
1. Check backend logs: `tail -f backend/app.log`
2. Ensure stable network connection
3. Increase timeout in config:
```json
{
  "mcpServers": {
    "aiveilix": {
      "command": "python",
      "args": ["-m", "app.mcp_stdio"],
      "timeout": 30000,
      "env": { ... }
    }
  }
}
```

---

**Issue:** "Permission denied errors"

**Solution:**
```bash
# Ensure Python has execute permissions
chmod +x $(which python3)

# Check file permissions
ls -la /path/to/AIveilix/backend/app/mcp_stdio.py

# Should be readable (644 or 755)
chmod 644 /path/to/AIveilix/backend/app/mcp_stdio.py
```

---

## ChatGPT Setup

**ChatGPT** can access AIveilix via OAuth2 integration. This allows ChatGPT to read your documents when needed.

**Status:** OAuth2 flow implemented, ChatGPT MCP support coming soon


### Prerequisites

- ✅ ChatGPT Plus or Team account
- ✅ AIveilix backend running
- ✅ OAuth2 client created

### Step 1: Create OAuth2 Client



1. Open **AIveilix Dashboard**
2. Click **Profile icon** → **Credentials** tab
3. Switch to **"OAuth Clients"** view
4. Click **"Create Credential"** → Select **"OAuth Client"**


**Fill in details:**

**Name:**
```
ChatGPT Integration
```

**Redirect URI:**
```
https://chat.openai.com/aip/oauth/callback
```

⚠️ **CRITICAL:** This URI must be EXACT. ChatGPT requires this specific callback URL.

**Scopes:**
- ☑️ **read** - View files
- ☑️ **query** - Search functionality
- ☑️ **chat** - Chat features

Click **"Create"**


**Save Credentials (ONE-TIME DISPLAY):**

```
Client ID:
oauth_client_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

Client Secret:
oauth_secret_x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6

⚠️ Copy and save these credentials now!
   They won't be shown again.
```

### Step 2: OAuth2 Endpoints

**Authorization URL:**
```
https://api.aiveilix.com/api/oauth/authorize
```

**Token URL:**
```
https://api.aiveilix.com/api/oauth/token
```

**User Info URL:**
```
https://api.aiveilix.com/api/oauth/me
```

**Development URLs (self-hosted):**
```
http://localhost:7223/api/oauth/authorize
http://localhost:7223/api/oauth/token
http://localhost:7223/api/oauth/me
```

### Step 3: Create ChatGPT Action


1. **Go to ChatGPT** (https://chat.openai.com)
2. Click **"Explore GPTs"** (left sidebar)
3. Click **"Create a GPT"** (top-right)
4. Go to **"Configure"** tab
5. Scroll to **"Actions"** section
6. Click **"Create new action"**

### Step 4: Add OpenAPI Schema

**Paste this OpenAPI specification:**

```yaml
openapi: 3.1.0
info:
  title: AIveilix MCP API
  description: Access your AIveilix knowledge vault from ChatGPT
  version: 1.0.0
servers:
  - url: https://api.aiveilix.com
    description: Production server
  - url: http://localhost:7223
    description: Development server (self-hosted)

paths:
  /mcp/buckets:
    get:
      operationId: listBuckets
      summary: List all accessible buckets
      description: Returns list of buckets the user has access to
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  buckets:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                        name:
                          type: string
                        description:
                          type: string
                        file_count:
                          type: integer
                        created_at:
                          type: string
                          format: date-time

  /mcp/buckets/{bucket_id}/files:
    get:
      operationId: listFiles
      summary: List files in bucket
      description: Returns all files in specified bucket
      parameters:
        - name: bucket_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  files:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        name:
                          type: string
                        size_bytes:
                          type: integer
                        status:
                          type: string

  /mcp/buckets/{bucket_id}/query:
    post:
      operationId: queryBucket
      summary: Semantic search in bucket
      description: Search for relevant content using AI embeddings
      parameters:
        - name: bucket_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                  description: Search query
                limit:
                  type: integer
                  description: Max results (default 5)
                  default: 5
              required:
                - query
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        file_id:
                          type: string
                        file_name:
                          type: string
                        content:
                          type: string
                        similarity:
                          type: number

  /mcp/buckets/{bucket_id}/chat:
    post:
      operationId: chatWithBucket
      summary: AI chat with bucket contents
      description: Ask questions about documents in bucket
      parameters:
        - name: bucket_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Your question
                conversation_id:
                  type: string
                  description: Continue previous conversation (optional)
              required:
                - message
      responses:
        '200':
          description: AI response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: AI's answer
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        file_name:
                          type: string
                        confidence:
                          type: string
                  conversation_id:
                    type: string

components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.aiveilix.com/api/oauth/authorize
          tokenUrl: https://api.aiveilix.com/api/oauth/token
          scopes:
            read: Read access to files and buckets
            query: Semantic search capability
            chat: AI chat features

security:
  - OAuth2:
      - read
      - query
      - chat
```


### Step 5: Configure OAuth2

**After pasting schema:**

1. Scroll to **"Authentication"** section
2. Select **"OAuth"**
3. Fill in OAuth details:


**Client ID:**
```
oauth_client_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Client Secret:**
```
oauth_secret_x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6
```

**Authorization URL:**
```
https://api.aiveilix.com/api/oauth/authorize
```

**Token URL:**
```
https://api.aiveilix.com/api/oauth/token
```

**Scope:**
```
read query chat
```

**Token Exchange Method:**
```
Basic authorization header
```

### Step 6: Test OAuth Flow


1. **Click "Test"** button in ChatGPT action config
2. **Redirected to AIveilix** authorization page:

```
┌─────────────────────────────────────────┐
│  Authorize ChatGPT                      │
│                                         │
│  ChatGPT Integration wants to:          │
│  ☑ Read your files and buckets          │
│  ☑ Search your documents                │
│  ☑ Chat with your documents             │
│                                         │
│  [Deny]  [Authorize]                    │
└─────────────────────────────────────────┘
```

3. **Click "Authorize"**
4. **Redirected back to ChatGPT** with success message
5. **OAuth token obtained** (valid for 60 minutes)

### Step 7: Use AIveilix in ChatGPT


**Example Conversations:**

```
You: "List my AIveilix buckets"

ChatGPT: [Calls listBuckets action]
"You have 3 buckets in AIveilix:

1. Work Projects - 45 files
2. Personal Notes - 12 files
3. Research Papers - 78 files

Which would you like to explore?"
```

```
You: "Search my Work Projects for authentication code"

ChatGPT: [Calls queryBucket action]
"I found authentication-related code in:

1. auth.py - JWT token generation
2. middleware.py - Route protection
3. tests/auth_test.py - Test suite

Here's the main authentication function:
[Shows code from your files]"
```

```
You: "Summarize all documents in Research Papers about neural networks"

ChatGPT: [Calls chatWithBucket action]
"I've analyzed your research papers on neural networks:

Key themes:
1. Convolutional architectures (5 papers)
2. Training optimization (3 papers)
3. Transfer learning (4 papers)

[Detailed summary with citations]"
```

### OAuth2 Flow Diagram

```
1. User initiates ChatGPT action
   ChatGPT → AIveilix: GET /api/oauth/authorize
                       ?client_id=...
                       &redirect_uri=https://chat.openai.com/aip/oauth/callback
                       &scope=read+query+chat
                       &state=random_state

2. AIveilix shows authorization page
   User clicks "Authorize"

3. AIveilix creates auth code
   AIveilix → ChatGPT: Redirect to callback
                       ?code=auth_code_here
                       &state=random_state

4. ChatGPT exchanges code for token
   ChatGPT → AIveilix: POST /api/oauth/token
                       client_id=...
                       client_secret=...
                       code=auth_code_here
                       grant_type=authorization_code

5. AIveilix returns tokens
   AIveilix → ChatGPT: {
                         "access_token": "...",
                         "refresh_token": "...",
                         "expires_in": 3600
                       }

6. ChatGPT uses access token
   ChatGPT → AIveilix: GET /mcp/buckets
                       Authorization: Bearer access_token

7. Token expires (60 min)
   ChatGPT refreshes token automatically
```

### Refresh Token Flow

**Automatic Refresh:**

When access token expires (60 minutes):

```
ChatGPT → AIveilix: POST /api/oauth/token
                    grant_type=refresh_token
                    refresh_token=...
                    client_id=...
                    client_secret=...

AIveilix → ChatGPT: {
                      "access_token": "new_token_here",
                      "refresh_token": "new_refresh_token",
                      "expires_in": 3600
                    }
```

Refresh tokens valid for **30 days**.

### Revoking Access

**To revoke ChatGPT's access:**

1. Go to **Profile → Credentials → OAuth Clients**
2. Find **"ChatGPT Integration"**
3. Click **"Revoke"** button
4. Confirm revocation
5. All tokens immediately invalidated
6. ChatGPT loses access


### Troubleshooting ChatGPT Integration

**Issue:** "Invalid redirect_uri"

**Solution:**
- Must use EXACT callback URL: `https://chat.openai.com/aip/oauth/callback`
- Check for typos, trailing slashes, http vs https
- Recreate OAuth client if needed

---

**Issue:** "Authorization failed"

**Solution:**
1. Check client_id and client_secret are correct
2. Verify OAuth client is active (not revoked)
3. Check backend logs for detailed error
4. Ensure scopes match (read, query, chat)

---

**Issue:** "Token expired"

**Solution:**
- Automatic refresh should work
- If failing, check refresh token is valid
- Revoke and re-authorize if stuck
- Check token expiry settings in `backend/app/config.py`

---

## Zed Editor Setup

**Zed** is a high-performance code editor with native MCP support. Lightning-fast integration with AIveilix.


### Prerequisites

- ✅ Zed installed (https://zed.dev)
- ✅ AIveilix backend running
- ✅ Python 3.10+ installed
- ✅ AIveilix API key created

### Step 1: Open Zed Settings

**macOS:**
- Press **Cmd+,** (Comma)
- Or Menu: **Zed → Settings**

**Linux/Windows:**
- Press **Ctrl+,**
- Or Menu: **File → Settings**


### Step 2: Configure MCP

**Locate MCP Settings:**

1. In Settings, search for **"MCP"** or **"Model Context Protocol"**
2. Or manually edit: **~/.config/zed/settings.json**

**Add AIveilix MCP Configuration:**

```json
{
  "language_models": {
    "anthropic": {
      "api_key": "your_claude_api_key"
    }
  },
  "context_servers": {
    "aiveilix": {
      "command": {
        "path": "python",
        "args": ["-m", "app.mcp_stdio"],
        "env": {
          "AIVEILIX_API_KEY": "aiveilix_sk_live_YOUR_KEY_HERE",
          "PYTHONPATH": "/absolute/path/to/AIveilix/backend"
        },
        "cwd": "/absolute/path/to/AIveilix/backend"
      }
    }
  }
}
```

**Example (macOS):**

```json
{
  "language_models": {
    "anthropic": {
      "api_key": "sk-ant-..."
    }
  },
  "context_servers": {
    "aiveilix": {
      "command": {
        "path": "/usr/local/bin/python3",
        "args": ["-m", "app.mcp_stdio"],
        "env": {
          "AIVEILIX_API_KEY": "aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
          "PYTHONPATH": "/Users/john/Projects/AIveilix/backend"
        },
        "cwd": "/Users/john/Projects/AIveilix/backend"
      }
    }
  }
}
```

### Step 3: Restart Zed

1. **Quit Zed** (**Cmd+Q** / **Ctrl+Q**)
2. **Reopen Zed**
3. MCP server launches automatically

### Step 4: Verify Connection

**Check Status:**

1. Open **Command Palette** (**Cmd+Shift+P** / **Ctrl+Shift+P**)
2. Type: **"MCP: Show Context Servers"**
3. Should see **"aiveilix"** with **Connected** status


### Step 5: Use AIveilix in Zed

**Assistant Panel:**

1. Open **Assistant** (**Cmd+?** / **Ctrl+?**)
2. Type `/` to see context commands
3. Type `/aiveilix` to access AIveilix


**Example Usage:**

```
/aiveilix list buckets

AI: "You have 3 buckets:
1. Work Projects (45 files)
2. Personal Notes (12 files)
3. Research Papers (78 files)"

---

/aiveilix search Work Projects "authentication flow"

AI: "Found in auth.py:
def authenticate_user(email, password):
    # JWT token generation
    ..."

---

/aiveilix chat Work Projects "Explain the architecture"

AI: "Based on architecture.pdf, the system uses:
1. FastAPI backend
2. React frontend
3. PostgreSQL database..."
```

### Inline Context

**While coding:**

```python
# Type: Cmd+. (Mac) or Ctrl+. (Windows/Linux)
# Ask: "How should I structure this based on @aiveilix Work Projects?"

def new_feature():
    # AI suggests code based on your docs
    pass
```

---

## Continue.dev (VS Code) Setup

**Continue** is an open-source AI coding assistant for VS Code with MCP support.


### Prerequisites

- ✅ VS Code installed
- ✅ Continue extension installed
- ✅ AIveilix backend running
- ✅ Python 3.10+ installed
- ✅ AIveilix API key created

### Step 1: Install Continue Extension

1. Open **VS Code**
2. Go to **Extensions** (Cmd+Shift+X / Ctrl+Shift+X)
3. Search: **"Continue"**
4. Click **"Install"** on **"Continue - AI Code Assistant"**


### Step 2: Configure Continue

**Open Continue Settings:**

1. Click **Continue icon** in VS Code sidebar (AI icon)
2. Click **"gear icon"** (settings) in Continue panel
3. Or edit directly: **~/.continue/config.json**


### Step 3: Add AIveilix Context Provider

**Edit config.json:**

```json
{
  "models": [
    {
      "title": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "apiKey": "your_claude_api_key"
    }
  ],
  "contextProviders": [
    {
      "name": "aiveilix",
      "params": {
        "command": "python",
        "args": ["-m", "app.mcp_stdio"],
        "env": {
          "AIVEILIX_API_KEY": "aiveilix_sk_live_YOUR_KEY_HERE",
          "PYTHONPATH": "/absolute/path/to/AIveilix/backend"
        },
        "cwd": "/absolute/path/to/AIveilix/backend"
      }
    }
  ]
}
```

**Example (Full Config):**

```json
{
  "models": [
    {
      "title": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "apiKey": "sk-ant-api03-..."
    },
    {
      "title": "GPT-4",
      "provider": "openai",
      "model": "gpt-4-turbo-preview",
      "apiKey": "sk-..."
    }
  ],
  "contextProviders": [
    {
      "name": "code",
      "params": {}
    },
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "terminal",
      "params": {}
    },
    {
      "name": "aiveilix",
      "params": {
        "command": "python3",
        "args": ["-m", "app.mcp_stdio"],
        "env": {
          "AIVEILIX_API_KEY": "aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
          "PYTHONPATH": "/Users/john/Projects/AIveilix/backend"
        },
        "cwd": "/Users/john/Projects/AIveilix/backend"
      }
    }
  ],
  "slashCommands": [
    {
      "name": "edit",
      "description": "Edit highlighted code"
    },
    {
      "name": "comment",
      "description": "Write comments"
    }
  ]
}
```

### Step 4: Reload VS Code

1. **Command Palette** (Cmd+Shift+P / Ctrl+Shift+P)
2. Type: **"Reload Window"**
3. Press Enter

### Step 5: Use AIveilix in Continue

**Chat Panel:**


1. Open **Continue panel** (sidebar)
2. Type **@aiveilix** in chat
3. Autocomplete shows AIveilix context
4. Ask questions

**Example:**

```
@aiveilix Work Projects

"How is authentication implemented?"

AI: [Reads from your docs]
"Authentication uses JWT tokens. Here's the flow:
1. User sends credentials
2. Server validates
3. JWT generated (60-min expiry)
4. Token stored in httpOnly cookie

Source: architecture.pdf, auth.py"
```

**Inline Edit:**

```python
# Highlight code
# Cmd+I (Mac) or Ctrl+I (Windows/Linux)
# Type: "Refactor this to match @aiveilix Work Projects/coding_standards.md"

def old_function():
    pass

# AI refactors based on your standards doc
```

---

## Custom Python Client

Build your own Python integration with AIveilix using the MCP HTTP API.



### Installation

```bash
pip install requests python-dotenv
```

### Basic Example

**File: `aiveilix_client.py`**

```python
import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIveilixClient:
    """AIveilix MCP HTTP Client"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize AIveilix client

        Args:
            api_key: AIveilix API key (or set AIVEILIX_API_KEY env var)
            base_url: Base URL (default: https://api.aiveilix.com)
        """
        self.api_key = api_key or os.getenv('AIVEILIX_API_KEY')
        if not self.api_key:
            raise ValueError("API key required. Set AIVEILIX_API_KEY env var or pass api_key parameter")

        self.base_url = base_url or os.getenv('AIVEILIX_BASE_URL', 'https://api.aiveilix.com')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def list_buckets(self) -> List[Dict]:
        """
        List all accessible buckets

        Returns:
            List of bucket objects
        """
        response = requests.get(
            f'{self.base_url}/mcp/buckets',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()['buckets']

    def list_files(self, bucket_id: str) -> List[Dict]:
        """
        List files in bucket

        Args:
            bucket_id: Bucket UUID

        Returns:
            List of file objects
        """
        response = requests.get(
            f'{self.base_url}/mcp/buckets/{bucket_id}/files',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()['files']

    def query(self, bucket_id: str, query: str, limit: int = 5) -> List[Dict]:
        """
        Semantic search in bucket

        Args:
            bucket_id: Bucket UUID
            query: Search query
            limit: Max results (default 5)

        Returns:
            List of search results
        """
        response = requests.post(
            f'{self.base_url}/mcp/buckets/{bucket_id}/query',
            headers=self.headers,
            json={
                'query': query,
                'limit': limit
            }
        )
        response.raise_for_status()
        return response.json()['results']

    def chat(
        self,
        bucket_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        AI chat with bucket contents

        Args:
            bucket_id: Bucket UUID
            message: Your question
            conversation_id: Continue previous conversation (optional)

        Returns:
            AI response with message and sources
        """
        response = requests.post(
            f'{self.base_url}/mcp/buckets/{bucket_id}/chat',
            headers=self.headers,
            json={
                'message': message,
                'conversation_id': conversation_id
            }
        )
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == '__main__':
    # Initialize client
    client = AIveilixClient()

    # List buckets
    print("📁 Your buckets:")
    buckets = client.list_buckets()
    for bucket in buckets:
        print(f"  - {bucket['name']} ({bucket['file_count']} files)")

    # Use first bucket
    if buckets:
        bucket_id = buckets[0]['id']

        # List files
        print(f"\n📄 Files in {buckets[0]['name']}:")
        files = client.list_files(bucket_id)
        for file in files:
            print(f"  - {file['name']} ({file['size_bytes']} bytes)")

        # Search
        print("\n🔍 Searching for 'authentication':")
        results = client.query(bucket_id, 'authentication', limit=3)
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. {result['file_name']} (similarity: {result['similarity']:.2f})")
            print(f"     {result['content'][:100]}...")

        # Chat
        print("\n💬 Asking question:")
        response = client.chat(bucket_id, "What are the main topics in these documents?")
        print(f"  AI: {response['message']}")
        if response.get('sources'):
            print(f"  Sources: {', '.join(s['file_name'] for s in response['sources'])}")
```

### Environment Setup

**Create `.env` file:**

```env
AIVEILIX_API_KEY=aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
# AIVEILIX_BASE_URL=http://localhost:7223  # Only needed for self-hosted
```

**Run:**

```bash
python aiveilix_client.py
```

### Advanced Example - RAG Pipeline

```python
from aiveilix_client import AIveilixClient
import openai

class RAGPipeline:
    """Retrieval-Augmented Generation using AIveilix"""

    def __init__(self, aiveilix_api_key: str, openai_api_key: str):
        self.aiveilix = AIveilixClient(api_key=aiveilix_api_key)
        openai.api_key = openai_api_key

    def ask(self, bucket_id: str, question: str) -> str:
        """
        Ask question with RAG

        1. Retrieve relevant context from AIveilix
        2. Augment prompt with context
        3. Generate answer with GPT-4
        """
        # Step 1: Retrieve context
        results = self.aiveilix.query(bucket_id, question, limit=5)

        # Step 2: Build context
        context = "\n\n".join([
            f"From {r['file_name']}:\n{r['content']}"
            for r in results
        ])

        # Step 3: Generate answer
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Answer questions based on the provided context. Include source citations."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ]
        )

        return response.choices[0].message.content


# Usage
rag = RAGPipeline(
    aiveilix_api_key='aiveilix_sk_live_...',
    openai_api_key='sk-...'
)

answer = rag.ask(
    bucket_id='550e8400-e29b-41d4-a716-446655440000',
    question='How does authentication work in our system?'
)
print(answer)
```

### Error Handling

```python
import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError

class AIveilixClient:
    # ... previous code ...

    def safe_query(self, bucket_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Query with error handling"""
        try:
            response = requests.post(
                f'{self.base_url}/mcp/buckets/{bucket_id}/query',
                headers=self.headers,
                json={'query': query, 'limit': limit},
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()
            return response.json()['results']

        except HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid API key or expired token")
            elif e.response.status_code == 403:
                raise ValueError("Access denied to this bucket")
            elif e.response.status_code == 404:
                raise ValueError(f"Bucket {bucket_id} not found")
            elif e.response.status_code == 429:
                raise ValueError("Rate limit exceeded. Wait before retrying.")
            else:
                raise ValueError(f"API error: {e.response.text}")

        except Timeout:
            raise ValueError("Request timed out. Check your connection.")

        except ConnectionError:
            raise ValueError("Cannot connect to AIveilix. Is the backend running?")
```

---

## Custom Node.js Client

Integrate AIveilix into your Node.js/JavaScript applications.


### Installation

```bash
npm install axios dotenv
```

### Basic Example

**File: `aiveilix-client.js`**

```javascript
const axios = require('axios');
require('dotenv').config();

class AIveilixClient {
  /**
   * Initialize AIveilix client
   * @param {string} apiKey - AIveilix API key (or set AIVEILIX_API_KEY env var)
   * @param {string} baseURL - Base URL (default: https://api.aiveilix.com)
   */
  constructor(apiKey = null, baseURL = null) {
    this.apiKey = apiKey || process.env.AIVEILIX_API_KEY;
    if (!this.apiKey) {
      throw new Error('API key required. Set AIVEILIX_API_KEY env var or pass apiKey parameter');
    }

    this.baseURL = baseURL || process.env.AIVEILIX_BASE_URL || 'https://api.aiveilix.com';
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000 // 30 seconds
    });
  }

  /**
   * List all accessible buckets
   * @returns {Promise<Array>} List of bucket objects
   */
  async listBuckets() {
    const response = await this.client.get('/mcp/buckets');
    return response.data.buckets;
  }

  /**
   * List files in bucket
   * @param {string} bucketId - Bucket UUID
   * @returns {Promise<Array>} List of file objects
   */
  async listFiles(bucketId) {
    const response = await this.client.get(`/mcp/buckets/${bucketId}/files`);
    return response.data.files;
  }

  /**
   * Semantic search in bucket
   * @param {string} bucketId - Bucket UUID
   * @param {string} query - Search query
   * @param {number} limit - Max results (default 5)
   * @returns {Promise<Array>} List of search results
   */
  async query(bucketId, query, limit = 5) {
    const response = await this.client.post(`/mcp/buckets/${bucketId}/query`, {
      query,
      limit
    });
    return response.data.results;
  }

  /**
   * AI chat with bucket contents
   * @param {string} bucketId - Bucket UUID
   * @param {string} message - Your question
   * @param {string} conversationId - Continue previous conversation (optional)
   * @returns {Promise<Object>} AI response with message and sources
   */
  async chat(bucketId, message, conversationId = null) {
    const response = await this.client.post(`/mcp/buckets/${bucketId}/chat`, {
      message,
      conversation_id: conversationId
    });
    return response.data;
  }
}

// Example usage
async function main() {
  const client = new AIveilixClient();

  try {
    // List buckets
    console.log('📁 Your buckets:');
    const buckets = await client.listBuckets();
    buckets.forEach(bucket => {
      console.log(`  - ${bucket.name} (${bucket.file_count} files)`);
    });

    if (buckets.length > 0) {
      const bucketId = buckets[0].id;

      // List files
      console.log(`\n📄 Files in ${buckets[0].name}:`);
      const files = await client.listFiles(bucketId);
      files.forEach(file => {
        console.log(`  - ${file.name} (${file.size_bytes} bytes)`);
      });

      // Search
      console.log('\n🔍 Searching for "authentication":');
      const results = await client.query(bucketId, 'authentication', 3);
      results.forEach((result, i) => {
        console.log(`\n  ${i + 1}. ${result.file_name} (similarity: ${result.similarity.toFixed(2)})`);
        console.log(`     ${result.content.substring(0, 100)}...`);
      });

      // Chat
      console.log('\n💬 Asking question:');
      const response = await client.chat(bucketId, 'What are the main topics?');
      console.log(`  AI: ${response.message}`);
      if (response.sources) {
        console.log(`  Sources: ${response.sources.map(s => s.file_name).join(', ')}`);
      }
    }

  } catch (error) {
    console.error('Error:', error.message);
    if (error.response) {
      console.error('Details:', error.response.data);
    }
  }
}

if (require.main === module) {
  main();
}

module.exports = AIveilixClient;
```

### Environment Setup

**Create `.env` file:**

```env
AIVEILIX_API_KEY=aiveilix_sk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
# AIVEILIX_BASE_URL=http://localhost:7223  # Only needed for self-hosted
```

**Run:**

```bash
node aiveilix-client.js
```

### TypeScript Version

**File: `aiveilix-client.ts`**

```typescript
import axios, { AxiosInstance } from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

interface Bucket {
  id: string;
  name: string;
  description: string;
  file_count: number;
  created_at: string;
}

interface File {
  id: string;
  name: string;
  size_bytes: number;
  status: string;
}

interface SearchResult {
  file_id: string;
  file_name: string;
  content: string;
  similarity: number;
}

interface ChatResponse {
  message: string;
  sources: Array<{
    file_name: string;
    confidence: string;
  }>;
  conversation_id: string;
}

class AIveilixClient {
  private client: AxiosInstance;

  constructor(apiKey?: string, baseURL?: string) {
    const key = apiKey || process.env.AIVEILIX_API_KEY;
    if (!key) {
      throw new Error('API key required');
    }

    this.client = axios.create({
      baseURL: baseURL || process.env.AIVEILIX_BASE_URL || 'https://api.aiveilix.com',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    });
  }

  async listBuckets(): Promise<Bucket[]> {
    const response = await this.client.get<{ buckets: Bucket[] }>('/mcp/buckets');
    return response.data.buckets;
  }

  async listFiles(bucketId: string): Promise<File[]> {
    const response = await this.client.get<{ files: File[] }>(`/mcp/buckets/${bucketId}/files`);
    return response.data.files;
  }

  async query(bucketId: string, query: string, limit: number = 5): Promise<SearchResult[]> {
    const response = await this.client.post<{ results: SearchResult[] }>(
      `/mcp/buckets/${bucketId}/query`,
      { query, limit }
    );
    return response.data.results;
  }

  async chat(bucketId: string, message: string, conversationId?: string): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(
      `/mcp/buckets/${bucketId}/chat`,
      { message, conversation_id: conversationId }
    );
    return response.data;
  }
}

export default AIveilixClient;
```

### Express.js Server Integration

```javascript
const express = require('express');
const AIveilixClient = require('./aiveilix-client');

const app = express();
app.use(express.json());

const aiveilix = new AIveilixClient();

// Endpoint: Search documents
app.post('/api/search', async (req, res) => {
  try {
    const { bucketId, query, limit } = req.body;
    const results = await aiveilix.query(bucketId, query, limit || 5);
    res.json({ success: true, results });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Chat with documents
app.post('/api/chat', async (req, res) => {
  try {
    const { bucketId, message, conversationId } = req.body;
    const response = await aiveilix.chat(bucketId, message, conversationId);
    res.json({ success: true, ...response });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: List buckets
app.get('/api/buckets', async (req, res) => {
  try {
    const buckets = await aiveilix.listBuckets();
    res.json({ success: true, buckets });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

---

## Postman & cURL Testing

Test AIveilix MCP endpoints directly with Postman or cURL.


### Postman Collection

**Import this collection:**

```json
{
  "info": {
    "name": "AIveilix MCP API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "List Buckets",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{AIVEILIX_API_KEY}}",
            "type": "text"
          }
        ],
        "url": {
          "raw": "{{BASE_URL}}/mcp/buckets",
          "host": ["{{BASE_URL}}"],
          "path": ["mcp", "buckets"]
        }
      }
    },
    {
      "name": "List Files in Bucket",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{AIVEILIX_API_KEY}}",
            "type": "text"
          }
        ],
        "url": {
          "raw": "{{BASE_URL}}/mcp/buckets/{{BUCKET_ID}}/files",
          "host": ["{{BASE_URL}}"],
          "path": ["mcp", "buckets", "{{BUCKET_ID}}", "files"]
        }
      }
    },
    {
      "name": "Semantic Search",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{AIVEILIX_API_KEY}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"authentication flow\",\n  \"limit\": 5\n}"
        },
        "url": {
          "raw": "{{BASE_URL}}/mcp/buckets/{{BUCKET_ID}}/query",
          "host": ["{{BASE_URL}}"],
          "path": ["mcp", "buckets", "{{BUCKET_ID}}", "query"]
        }
      }
    },
    {
      "name": "Chat with Bucket",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{AIVEILIX_API_KEY}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"What are the main topics in these documents?\",\n  \"conversation_id\": null\n}"
        },
        "url": {
          "raw": "{{BASE_URL}}/mcp/buckets/{{BUCKET_ID}}/chat",
          "host": ["{{BASE_URL}}"],
          "path": ["mcp", "buckets", "{{BUCKET_ID}}", "chat"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "BASE_URL",
      "value": "https://api.aiveilix.com"
    },
    {
      "key": "AIVEILIX_API_KEY",
      "value": "aiveilix_sk_live_YOUR_KEY_HERE"
    },
    {
      "key": "BUCKET_ID",
      "value": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

### cURL Examples

**List Buckets:**

```bash
curl -X GET "https://api.aiveilix.com/mcp/buckets" \
  -H "Authorization: Bearer aiveilix_sk_live_YOUR_KEY_HERE" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "buckets": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Work Projects",
      "description": "All work documents",
      "file_count": 45,
      "total_size_bytes": 234567890,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

**List Files:**

```bash
curl -X GET "https://api.aiveilix.com/mcp/buckets/550e8400-e29b-41d4-a716-446655440000/files" \
  -H "Authorization: Bearer aiveilix_sk_live_YOUR_KEY_HERE"
```

**Response:**
```json
{
  "files": [
    {
      "id": "abc123-def456-ghi789",
      "name": "architecture.pdf",
      "size_bytes": 2048000,
      "mime_type": "application/pdf",
      "status": "ready",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

**Semantic Search:**

```bash
curl -X POST "https://api.aiveilix.com/mcp/buckets/550e8400-e29b-41d4-a716-446655440000/query" \
  -H "Authorization: Bearer aiveilix_sk_live_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication flow",
    "limit": 5
  }'
```

**Response:**
```json
{
  "results": [
    {
      "file_id": "abc123",
      "file_name": "auth.py",
      "content": "def authenticate_user(email, password):\n    # Validates credentials and generates JWT token\n    ...",
      "similarity": 0.89,
      "chunk_index": 5,
      "page_number": null
    }
  ]
}
```

---

**Chat:**

```bash
curl -X POST "https://api.aiveilix.com/mcp/buckets/550e8400-e29b-41d4-a716-446655440000/chat" \
  -H "Authorization: Bearer aiveilix_sk_live_YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main topics in these documents?",
    "conversation_id": null
  }'
```

**Response:**
```json
{
  "message": "Based on your documents, the main topics are:\n1. Authentication flows\n2. Database schema\n3. API endpoints\n4. Frontend components",
  "sources": [
    {
      "type": "analysis",
      "file_name": "architecture.pdf",
      "confidence": "high"
    },
    {
      "type": "chunk",
      "file_name": "readme.md",
      "confidence": "medium"
    }
  ],
  "conversation_id": "conv_uuid_here"
}
```

---

**Bash Script Example:**

```bash
#!/bin/bash

# Configuration
API_KEY="aiveilix_sk_live_YOUR_KEY_HERE"
BASE_URL="https://api.aiveilix.com"

# List buckets
echo "📁 Fetching buckets..."
BUCKETS=$(curl -s -X GET "$BASE_URL/mcp/buckets" \
  -H "Authorization: Bearer $API_KEY")

echo "$BUCKETS" | jq '.buckets[] | {name: .name, files: .file_count}'

# Get first bucket ID
BUCKET_ID=$(echo "$BUCKETS" | jq -r '.buckets[0].id')

# Search in bucket
echo -e "\n🔍 Searching for 'authentication'..."
curl -s -X POST "$BASE_URL/mcp/buckets/$BUCKET_ID/query" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "limit": 3}' \
  | jq '.results[] | {file: .file_name, similarity: .similarity}'
```

---

## Generic MCP Client

Integrate AIveilix with any MCP-compatible application.

### MCP Protocol Specification

**AIveilix implements MCP v1.0** with:

**Resources:**
```
aiveilix://buckets
aiveilix://buckets/{bucket_id}
aiveilix://buckets/{bucket_id}/files
aiveilix://buckets/{bucket_id}/files/{file_id}
```

**Tools:**
```
- aiveilix_list_buckets()
- aiveilix_list_files(bucket_id: string)
- aiveilix_query(bucket_id: string, query: string, limit: integer)
- aiveilix_chat(bucket_id: string, message: string, conversation_id?: string)
```

**Prompts:**
```
- summarize_bucket(bucket_id: string)
- find_information(bucket_id: string, topic: string)
- compare_files(file_id_1: string, file_id_2: string)
```

### Stdio Transport

**Launch MCP server:**

```bash
cd /path/to/AIveilix/backend
AIVEILIX_API_KEY=your_key python -m app.mcp_stdio
```

**Communication:**
- **Input:** stdin (JSON-RPC 2.0)
- **Output:** stdout (JSON-RPC 2.0)
- **Errors:** stderr

**Example Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "aiveilix_list_buckets",
    "arguments": {}
  }
}
```

**Example Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "You have 3 buckets:\n1. Work Projects (45 files)\n2. Personal Notes (12 files)\n3. Research Papers (78 files)"
      }
    ]
  }
}
```

### HTTP Transport

**Base URL:** `https://api.aiveilix.com`

**Authentication:** `Authorization: Bearer {api_key}`

**Rate Limiting:** 100 requests/hour per API key (configurable)

**Endpoints:** See Custom Python/Node.js Client sections above

---

## Troubleshooting

### Common Issues & Solutions

**Issue:** "Backend not running"

**Symptoms:**
- `Connection refused`
- `ECONNREFUSED`
- `Cannot connect to API` or connection errors

**Solution:**
```bash
# 1. Verify API is accessible
curl https://api.aiveilix.com

# 2. Check your internet connection
ping api.aiveilix.com

# 3. Verify API key is valid (check expiration in dashboard)

# 4. Check firewall/proxy settings
lsof -i :7223  # macOS/Linux
netstat -ano | findstr :7223  # Windows
```

---

**Issue:** "Invalid API key"

**Symptoms:**
- `401 Unauthorized`
- `Invalid or expired API key`
- `Authentication failed`

**Solution:**
1. Verify key format: `aiveilix_sk_live_...`
2. Check key in Profile → Credentials → API Keys
3. Ensure key is Active (not Revoked)
4. Regenerate key if lost
5. Check for extra spaces/quotes in config

---

**Issue:** "Rate limit exceeded"

**Symptoms:**
- `429 Too Many Requests`
- `Rate limit exceeded`

**Solution:**
```python
# Default: 100 requests/hour per key

# Option 1: Wait 1 hour for reset
# Option 2: Create additional API key
# Option 3: Increase limit in backend/app/config.py:
MCP_RATE_LIMIT = 200  # requests per hour
```

---

**Issue:** "Bucket not found"

**Symptoms:**
- `404 Not Found`
- `Bucket does not exist`

**Solution:**
1. List buckets to get correct ID
2. Verify bucket ownership
3. Check API key has access to bucket
4. Ensure bucket wasn't deleted

---

**Issue:** "MCP server crashes immediately"

**Symptoms:**
- Process exits after launch
- No output from stdio
- Connection lost

**Solution:**
```bash
# 1. Test server manually
cd backend
AIVEILIX_API_KEY=your_key python -m app.mcp_stdio

# 2. Check for Python errors
python -m app.mcp_stdio 2>&1 | tee mcp.log

# 3. Verify dependencies
pip install -r requirements.txt

# 4. Check Python version
python --version  # Should be 3.10+

# 5. Inspect logs
cat mcp.log
```

---

**Issue:** "CORS errors (web apps)"

**Symptoms:**
- `Access-Control-Allow-Origin` error
- `CORS policy blocked`

**Solution:**

**Backend** (`backend/app/main.py` already configured):
```python
# CORS middleware allows:
- https://aiveilix.com (production frontend)
- https://chat.openai.com (ChatGPT)
- https://claude.ai (Claude)
- http://localhost:6677 (development only)

# Example CORS configuration:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aiveilix.com",
        "https://chat.openai.com",
        "https://claude.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

**Issue:** "SSL/TLS certificate errors"

**Symptoms:**
- `SSL: CERTIFICATE_VERIFY_FAILED`
- `unable to get local issuer certificate`

**Solution:**
```bash
# Development only - disable SSL verification
# Python:
import requests
requests.get(url, verify=False)

# Node.js:
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'

# Production - use proper SSL
# Get certificate from Let's Encrypt, etc.
```

---

### Debug Mode

**Enable detailed logging:**

**Backend:**

Edit `backend/app/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**MCP Stdio:**

```bash
# Run with verbose output
PYTHONUNBUFFERED=1 AIVEILIX_API_KEY=your_key python -m app.mcp_stdio 2>&1 | tee mcp_debug.log
```

**Check logs:**
```bash
# Backend logs
tail -f backend/app.log

# MCP stdio logs
tail -f mcp_debug.log

# System logs (macOS)
log stream --predicate 'process == "python"' --level debug
```

---

### Getting Help

**Resources:**
- **Documentation:** `/doc` page on AIveilix dashboard
- **GitHub Issues:** https://github.com/anthropics/claude-code/issues (for MCP spec)
- **Support Email:** support@aiveilix.com
- **Community:** discord.gg/aiveilix (if available)

**When asking for help, include:**
1. Error message (full traceback)
2. API endpoint/tool used
3. Request/response (sanitize API key!)
4. Environment (OS, Python version, Node version)
5. Steps to reproduce

---

**End of Integrations Guide**

You now have AIveilix connected to all your favorite tools! 🚀
