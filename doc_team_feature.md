# Team Feature - Detailed Implementation Guide

## Overview
The Team Feature allows workspace owners to invite team members, assign per-bucket permissions (view/chat/upload/delete), and track every member's actions with a unique color. Members log in with auto-generated `name@aiveilix.com` accounts and see only their assigned buckets.

---

## Architecture

```
Owner creates member → Supabase Auth account (name@aiveilix.com)
                     → team_members record
                     → profiles updated (is_team_member=true)

Member logs in → /api/auth/login (same login page)
              → /api/auth/me returns team info
              → Frontend stores: is_team_member, team_owner_id, color, name
              → Dashboard shows only assigned buckets

Member actions → effective_user_id = owner_id (queries owner's data)
              → Permission checks per bucket (can_view/chat/upload/delete)
              → Color/name tracked on messages + files
              → Activity logged in team_activity_log
```

---

## Database (Migration)

**File:** `supabase/migrations/009_add_team_tables.sql`

### New Tables

#### `team_members`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| owner_id | UUID | FK to auth.users - the workspace owner |
| member_id | UUID | FK to auth.users - the created auth account |
| name | TEXT | Display name |
| real_email | TEXT | Member's personal email (for reference) |
| aiveilix_email | TEXT | Auto-generated login email (name@aiveilix.com), UNIQUE |
| color | TEXT | Hex color for tracking (e.g. #A78BFA) |
| show_name | BOOLEAN | Admin toggle: show name on hover (default true) |
| is_active | BOOLEAN | Soft delete flag (default true) |
| removed_at | TIMESTAMPTZ | When member was deactivated |
| created_at / updated_at | TIMESTAMPTZ | Timestamps |

#### `team_bucket_access`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| team_member_id | UUID | FK to team_members |
| bucket_id | UUID | FK to buckets |
| can_view | BOOLEAN | Can see bucket and files |
| can_chat | BOOLEAN | Can send chat messages |
| can_upload | BOOLEAN | Can upload files |
| can_delete | BOOLEAN | Can delete files |
| UNIQUE(team_member_id, bucket_id) | | One permission set per member per bucket |

#### `team_activity_log`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| owner_id | UUID | Workspace owner |
| member_id | UUID | Auth user who performed action |
| team_member_id | UUID | FK to team_members |
| bucket_id | UUID | Which bucket (nullable) |
| action_type | TEXT | file_upload, file_delete, chat_message, api_key_create |
| resource_id | TEXT | ID of affected resource |
| resource_name | TEXT | Name of affected resource |
| member_color | TEXT | Snapshot of member's color at time of action |
| member_name | TEXT | Snapshot of member's name at time of action |
| metadata | JSONB | Extra data |
| created_at | TIMESTAMPTZ | When it happened |

### Modified Existing Tables

- **profiles**: Added `is_team_member` (bool), `team_owner_id` (UUID)
- **files**: Added `uploaded_by_member_id`, `uploaded_by_color`, `uploaded_by_name`
- **messages**: Added `sent_by_member_id`, `sent_by_color`, `sent_by_name`

### RLS Policies
- Owners can manage their team_members, team_bucket_access, team_activity_log
- Members can SELECT their own records
- Activity log: both owner and member can insert

---

## Backend

### Models
**File:** `backend/app/models/team.py`

Pydantic models for request/response:
- `AddTeamMemberRequest` - name, real_email, password, color
- `UpdateTeamMemberRequest` - color, show_name, is_active (all optional)
- `BucketPermissions` - bucket_id, can_view, can_chat, can_upload, can_delete
- `AssignBucketsRequest` - list of BucketPermissions
- `TeamMemberResponse` - full member details + bucket_count
- `TeamBucketAccessResponse` - permission details per bucket
- `TeamActivityLogEntry` - activity record
- `TeamInfoResponse` - for /me endpoint (is_team_member, owner info, color, permissions)

### Team Service
**File:** `backend/app/services/team_service.py`

Core functions:

| Function | What it does |
|----------|-------------|
| `get_team_member_context(user_id)` | Checks if user is a team member. Returns `{owner_id, team_member_id, color, name, show_name}` or `None` |
| `get_effective_user_id(user_id)` | Returns `owner_id` for members, `user_id` for owners. This is the KEY pattern - all DB queries use this to access owner's data |
| `check_bucket_permission(user_id, bucket_id, permission)` | Returns `True/False`. Owners always have all permissions. Members checked against team_bucket_access |
| `get_member_accessible_buckets(user_id)` | Returns list of bucket IDs member can access, or `None` for owners (meaning all) |
| `log_team_activity(...)` | Inserts into team_activity_log |
| `create_team_member_auth_account(name, password)` | Creates Supabase Auth user with `name@aiveilix.com`. Handles duplicates by appending counter |
| `delete_team_member_auth_account(member_user_id)` | Deletes the auth account via admin API |

### Team Router
**File:** `backend/app/routers/team.py`
**Registered at:** `/api/team` in `backend/app/main.py`

| Endpoint | Method | Who | Description |
|----------|--------|-----|-------------|
| `/api/team/members` | POST | Owner | Add team member (creates auth account, inserts record, updates profile, sends notification) |
| `/api/team/members` | GET | Owner | List all team members with bucket_count |
| `/api/team/members/{id}` | GET | Owner | Get member details + bucket access list |
| `/api/team/members/{id}` | PATCH | Owner | Update color, show_name, is_active |
| `/api/team/members/{id}` | DELETE | Owner | Soft-delete member (is_active=false, deletes auth account, color/name stays on historical data) |
| `/api/team/members/{id}/buckets` | POST | Owner | Assign bucket permissions (bulk upsert) |
| `/api/team/members/{id}/buckets` | GET | Owner | Get member's bucket access |
| `/api/team/members/{id}/buckets/{bucket_id}` | DELETE | Owner | Remove specific bucket access |
| `/api/team/activity` | GET | Owner | Activity log (filterable by member_id, bucket_id, limit) |
| `/api/team/me` | GET | Member | Get own team info (color, name, permissions, owner info) |

### Modified Routers

#### Auth Router (`backend/app/routers/auth.py`)
- **POST /signup**: Blocks if `real_email` exists in team_members → "You have a team member account"
- **GET /me**: Returns `is_team_member`, `team_owner_id`, `team_member_id`, `team_member_color`, `team_member_name`
- **POST /change-password**: Blocks for team members → 403 "Contact your team owner"
- **POST /delete-account**: Blocks for team members → 403 "Contact your team owner"

#### Buckets Router (`backend/app/routers/buckets.py`)
- **GET /**: Uses `effective_uid` + filters by `get_member_accessible_buckets()` for members
- **POST /**: Blocks team members → 403
- **GET /{id}**: Uses `effective_uid` + checks `can_view` permission
- **DELETE /{id}**: Blocks team members → 403

#### Files Router (`backend/app/routers/files.py`)
- **POST /upload**: Uses `effective_uid`, checks `can_upload`, sets `uploaded_by_color/name`, logs activity
- **GET /files**: Uses `effective_uid`, checks `can_view`, returns `uploaded_by_color/name` in response
- **DELETE /files/{id}**: Uses `effective_uid`, checks `can_delete`, logs activity

#### Chat Router (`backend/app/routers/chat.py`)
- **POST /chat**: Uses `effective_uid`, checks `can_chat`, sets `sent_by_color/name` on user message, logs activity
- **GET /conversations**: Uses `effective_uid`, checks `can_view`
- **GET /messages**: Uses `effective_uid` for conversation ownership check

#### API Keys Router (`backend/app/routers/api_keys.py`)
- **POST /**: Uses `effective_uid`, forces `allowed_buckets` to member's assigned buckets, logs activity
- **GET /**: Uses `effective_uid`
- **DELETE /{id}**: Uses `effective_uid`

#### Files Model (`backend/app/models/files.py`)
- Added `uploaded_by_color` and `uploaded_by_name` Optional[str] fields to `FileResponse`

### Notifications
**File:** `backend/app/services/notifications.py`

Added helpers:
- `create_team_member_added_notification(owner_id, member_name, member_color)`
- `create_team_member_removed_notification(owner_id, member_name)`
- `create_team_invite_notification(member_user_id, owner_name)`

---

## Frontend

### API Service
**File:** `frontend/src/services/api.js`

Added `teamAPI` object:
```
teamAPI.listMembers()
teamAPI.getMember(memberId)
teamAPI.addMember(name, realEmail, password, color)
teamAPI.updateMember(memberId, data)
teamAPI.removeMember(memberId)
teamAPI.getMemberBuckets(memberId)
teamAPI.assignBuckets(memberId, permissions)
teamAPI.removeBucketAccess(memberId, bucketId)
teamAPI.getActivity(memberId, bucketId, limit)
teamAPI.getMyTeamInfo()
```

Also fixed the 401 interceptor to not redirect when already on `/login` page (was causing infinite redirect loop).

### Auth Context
**File:** `frontend/src/context/AuthContext.jsx`

After login, fetches `/api/auth/me` to get team info and enriches user object:
- `is_team_member`, `team_owner_id`, `team_member_id`, `team_member_color`, `team_member_name`
- Exposes `isTeamMember` and `teamOwnerColor` from context

### New Components

#### AddTeamMemberModal
**File:** `frontend/src/components/AddTeamMemberModal.jsx`
- Modal with inputs: name, real email, password
- 16 preset color grid + custom hex input
- Follows existing modal pattern (rounded-3xl, backdrop-blur-xl)

#### TeamMemberBucketPermissions
**File:** `frontend/src/components/TeamMemberBucketPermissions.jsx`
- Lists all owner's buckets
- Toggle buttons per bucket: View, Chat, Upload, Delete
- Save calls `teamAPI.assignBuckets()`

#### TeamActivityFeed
**File:** `frontend/src/components/TeamActivityFeed.jsx`
- Shows recent team activity
- Each entry: colored dot + member name + action description + relative timestamp
- Filterable by memberId and bucketId props

### Modified Components

#### ProfileModal (`frontend/src/components/ProfileModal.jsx`)
- Added "Team" tab (only visible for owners, not team members)
- Team tab shows: member list with color dots, expandable details per member
- Inline bucket permissions management
- Toggle show_name per member
- Remove member button
- Activity feed at bottom
- Add Member button → opens AddTeamMemberModal

#### ChatPanel (`frontend/src/components/ChatPanel.jsx`)
- User message bubbles use member's color for border (inline style)
- Member name hidden by default, appears on hover (`group-hover` opacity)
- Loaded messages include `sent_by_color` and `sent_by_name`

#### FilesCard (`frontend/src/components/FilesCard.jsx`)
- Added `canDelete` prop to conditionally show/hide delete buttons
- Root files show colored dot next to filename if `uploaded_by_color` exists
- Dot has hover title with member name

#### Dashboard (`frontend/src/pages/Dashboard.jsx`)
- Team member banner at top ("Team member workspace")
- "Create Bucket" button hidden for team members
- Team member count badge next to welcome message (for owners)

#### Bucket Page (`frontend/src/pages/Bucket.jsx`)
- Imports AuthContext for team awareness
- Passes team info context to child components

---

## Key Design Pattern: effective_user_id

The most important pattern is `get_effective_user_id(user_id)`:

```
Owner logs in    → effective_uid = their own user_id
Member logs in   → effective_uid = owner's user_id

All DB queries use effective_uid:
  supabase.table("buckets").eq("user_id", effective_uid)  → queries OWNER's buckets
  supabase.table("files").eq("user_id", effective_uid)    → queries OWNER's files
  supabase.table("chunks").eq("user_id", effective_uid)   → queries OWNER's chunks
```

This means team members transparently access the owner's data without any data duplication.

---

## Member Lifecycle

```
1. Owner adds member (Profile → Team tab → Add Member)
   → Supabase Auth account created (name@aiveilix.com)
   → team_members record inserted
   → profiles updated (is_team_member=true, team_owner_id=owner)
   → Notification sent to owner

2. Owner assigns buckets (Team tab → member → Manage Permissions)
   → team_bucket_access records created/updated

3. Member logs in (same /login page, using name@aiveilix.com + password)
   → /api/auth/me returns team context
   → Dashboard shows limited view (only assigned buckets)

4. Member works (chat, upload, delete within permissions)
   → All queries use owner's user_id
   → Color/name tracked on messages and files
   → Activity logged

5. Owner removes member (Team tab → member → Remove)
   → is_active = false, removed_at = now
   → Auth account deleted (can't login anymore)
   → Historical messages/files KEEP the color/name (ghost trace)
```

---

## File Summary

### New Files (8)
| File | Description |
|------|-------------|
| `supabase/migrations/009_add_team_tables.sql` | DB migration (3 tables, column additions, indexes, RLS) |
| `backend/app/models/team.py` | Pydantic request/response models |
| `backend/app/services/team_service.py` | Core team logic (effective_uid, permissions, auth accounts) |
| `backend/app/routers/team.py` | REST API (10 endpoints) |
| `backend/app/dependencies.py` | UserContext class |
| `frontend/src/components/AddTeamMemberModal.jsx` | Add member form with color picker |
| `frontend/src/components/TeamMemberBucketPermissions.jsx` | Per-bucket permission toggles |
| `frontend/src/components/TeamActivityFeed.jsx` | Activity feed with colored dots |

### Modified Files (14)
| File | What Changed |
|------|-------------|
| `backend/app/main.py` | Registered team router at /api/team |
| `backend/app/routers/auth.py` | Signup block, /me enrichment, password/delete blocks |
| `backend/app/routers/buckets.py` | effective_uid, member filtering, create/delete blocks |
| `backend/app/routers/files.py` | Permissions, color tracking, activity logging |
| `backend/app/routers/chat.py` | Permissions, color tracking, activity logging, fixed messages endpoint |
| `backend/app/routers/api_keys.py` | effective_uid, forced bucket scoping |
| `backend/app/models/files.py` | Added uploaded_by_color/name to FileResponse |
| `backend/app/services/notifications.py` | 3 new team notification helpers |
| `frontend/src/services/api.js` | teamAPI methods, fixed 401 interceptor loop |
| `frontend/src/context/AuthContext.jsx` | Team info enrichment after login |
| `frontend/src/components/ProfileModal.jsx` | Team tab with member management |
| `frontend/src/components/ChatPanel.jsx` | Member color on bubbles, name on hover |
| `frontend/src/components/FilesCard.jsx` | Color dots on files, canDelete prop |
| `frontend/src/pages/Dashboard.jsx` | Team member banner, hidden create button, member count |
| `frontend/src/pages/Bucket.jsx` | AuthContext import for team awareness |
