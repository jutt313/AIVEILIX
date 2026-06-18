# Aiveilix — UX Flow

> This document describes the complete user experience flow for Aiveilix. It covers every screen, journey, interaction, and state a user will encounter from landing to daily use.

---

## 1. Landing Page

The first thing a new or returning user sees.

**Sections on the page:**
- Hero section — headline, subheadline, call to action buttons (Get Started, Login)
- How it works — 3 step explanation (Upload, Connect, Query)
- Features section — key product features
- Pricing section — Individual, Team, Enterprise plans with comparison table
- Testimonials section
- Footer — links to Privacy Policy, Terms of Service, Tokushoho

**User actions:**
- Click "Get Started" → goes to Signup page
- Click "Login" → goes to Login page
- Click pricing plan → goes to Signup page with plan pre-selected

---

## 2. Auth Flow

### 2.1 Signup Page

**Fields:**
- Full name
- Email address
- Password
- Confirm password

**Options:**
- Continue with Google
- Continue with GitHub

**Flow:**
```
User fills form and clicks "Create Account"
        |
        v
Validation runs (email format, password strength)
        |
        v
Account created in PostgreSQL
        |
        v
Verification email sent
        |
        v
User sees: "Please check your email to verify your account"
        |
        v
User clicks verification link
        |
        v
Account verified → redirect to Onboarding Flow
```

---

### 2.2 Login Page

**Fields:**
- Email address
- Password

**Options:**
- Continue with Google
- Continue with GitHub
- Forgot password link

**Flow:**
```
User enters email + password
        |
        v
If 5 failed attempts in last hour → show lockout message
"Too many failed attempts. Please try again in 1 hour."
        |
        v
If credentials correct and 2FA enabled → go to 2FA screen
        |
        v
If credentials correct and no 2FA → redirect to Dashboard
```

---

### 2.3 Two-Factor Authentication Screen

Shown only when 2FA is enabled on the account.

**Flow:**
```
User sees: "Enter the 6-digit code from your authenticator app"
        |
        v
User opens Google Authenticator / Authy
        |
        v
User enters 6-digit code
        |
        v
If correct → redirect to Dashboard
If wrong → show error, allow retry
```

---

### 2.4 Forgot Password Page

**Flow:**
```
User clicks "Forgot Password" on login page
        |
        v
User enters email address
        |
        v
Email sent with reset link (expires in 1 hour)
        |
        v
User clicks link → goes to Reset Password page
        |
        v
User enters new password + confirm password
        |
        v
Password updated → redirect to Login page
```

---

## 3. Onboarding Flow

Shown only on first login after signup. Helps personalize the experience.

### Step 1 — How will you use Aiveilix?
- For personal use
- For work or business
- For building AI agents
- Other

### Step 2 — Why do you need Aiveilix?
- I want persistent memory for my AI tools
- I want to search my documents with AI
- I want to connect my docs to Claude or ChatGPT
- Other

### Step 3 — How did you hear about us?
- Twitter / X
- YouTube
- Friend or colleague
- Google Search
- Other

### Step 4 — Set up your profile
- Upload profile picture
- Confirm display name

**Flow:**
```
User completes all steps
        |
        v
Profile saved to PostgreSQL
        |
        v
Redirect to Dashboard
        |
        v
Welcome message shown: "Your first bucket is ready to create!"
```

---

## 4. Dashboard

The main home screen after login. Shows an overview of all buckets and account activity.

### Layout

```
+—————————————————————————————————————+
| Logo    Search bar    Notifications  Profile |
+—————————————————————————————————————+
|                                             |
|   Usage Graphs                              |
|   (Storage used, Files count,               |
|    Chat messages, MCP calls)                |
|                                             |
|   [+ Create New Bucket]                     |
|                                             |
|   Your Buckets                              |
|   [ Bucket Card ] [ Bucket Card ] ...       |
|                                             |
+—————————————————————————————————————+
```

### Usage Graphs

Four graphs displayed at the top of the dashboard:
- Storage used vs storage limit
- Total files uploaded this month
- Total chat messages sent this month
- Total MCP calls this month

### Notifications Dropdown

Triggered by clicking the bell icon in the top bar.

**Notification types:**
- File processing complete
- File processing failed (with retry option)
- Storage limit warning (80% used)
- New team member accepted invite
- Billing payment successful
- Billing payment failed

### Light / Dark Mode Toggle

Available in the top bar. Preference saved to `profiles.theme` in PostgreSQL.

### Create New Bucket Button

```
User clicks "+ Create New Bucket"
        |
        v
Modal opens with fields:
- Bucket name (required)
- Description (optional)
- Color picker
- Icon picker
        |
        v
User clicks "Create"
        |
        v
Bucket created in PostgreSQL
MCP URL generated automatically
        |
        v
User redirected to the new Bucket Page
```

### Bucket Cards

Each bucket shows:
- Bucket name and icon
- Number of files
- Storage used
- Last activity time
- Click → goes to Bucket Page

---

## 5. Profile Popup

Opened by clicking the user avatar in the top bar. A slide-in panel from the right side.

### Sections

**Profile Section:**
- Profile picture (click to upload new one)
- Full name (editable)
- Email address (read only)
- Bio (editable)
- Save changes button

**Security Section:**
- Change password
  - Current password
  - New password
  - Confirm new password
- Two-Factor Authentication
  - Enable 2FA button (shows QR code flow)
  - Disable 2FA button (requires TOTP code confirmation)

**Preferences Section:**
- Theme toggle (light / dark)
- Language selector
- Timezone selector

**Billing Section:**
- Current plan (Individual / Team / Enterprise)
- Storage used vs limit
- Upgrade plan button
- Cancel subscription button
- Payment history list

**Danger Zone:**
- Delete account button (requires password confirmation)

---

## 6. Bucket Page

The main workspace for a single bucket.

### Layout

```
+————————————————————————————————————+
| Back   Bucket Name   Settings   MCP URL |
+————————————————————————————————————+
|                    |                      |
|   LEFT PANEL       |   RIGHT PANEL        |
|                    |                      |
|   Upload Button    |   Chat Interface     |
|                    |                      |
|   Search files     |   Max 20 conversation|
|                    |   threads per bucket |
|   Categories       |                      |
|   - All Files      |   Unlimited messages |
|   - Category 1     |   per conversation   |
|   - Category 2     |                      |
|                    |                      |
|   File List        |                      |
|   [ File Card ]    |                      |
|   [ File Card ]    |                      |
|   [ File Card ]    |                      |
|                    |                      |
+————————————————————————————————————+
```

### Left Panel — File Management

**Upload Button:**
```
User clicks "Upload Files"
        |
        v
File picker opens (supports bulk upload)
        |
        v
Files selected → upload starts immediately
        |
        v
Progress bar shown per file
        |
        v
File appears in list with status: "Processing"
        |
        v
Status updates in real time:
Processing → Ready (or Failed with retry option)
```

**File Cards show:**
- File name and type icon
- File size
- Processing status
- Upload date
- Click → goes to Doc Page

**Categories:**
- Default: All Files
- User can create categories and assign files to them
- Color-coded

### Right Panel — Chat Interface

**Conversation threads:**
- Max **20 conversation threads** per bucket
- Each thread has an auto-generated title
- Inside each thread, the user can send **unlimited messages**
- There is no message limit per conversation — users can chat as much as they want (1000+ messages is fine)

**Chat behavior:**
- User types question → RAG pipeline runs → AI answers
- Sources shown below each answer (file name, page number)
- New conversation button
- Conversation thread list on the left side of the chat panel

**Empty state (no files yet):**
```
"Upload your first file to start chatting with your bucket."
```

**Empty state (no conversations yet):**
```
"Start a new conversation to chat with your documents."
```

**Thread limit reached state (20/20):**
```
"You have reached the maximum of 20 conversation threads for this bucket.
 Delete an old thread to start a new one."
```

> Note: The limit is on the number of conversation threads (20 max), not on the number of messages. Once inside a thread, the user can send unlimited messages.

### MCP URL Button

- Shows the bucket MCP URL
- Copy to clipboard button
- Regenerate token button
- Revoke access button

---

## 7. Doc Page

Opened when user clicks on a file in the bucket.

### Layout

```
+————————————————————————————————+
| Back to Bucket   File Name      |
+————————————————————————————————+
|                                 |
|   File Details                  |
|   - Name, type, size, pages     |
|   - Upload date                 |
|   - Status                      |
|                                 |
|   AI Summary                    |
|   (auto-generated summary       |
|    of the full file)            |
|                                 |
|   Chunks List                   |
|   - Page number                 |
|   - Chunk content preview       |
|   - Nearby image info           |
|                                 |
|   File Versions                 |
|   - Version history list        |
|   - Re-upload new version       |
|                                 |
+————————————————————————————————+
```

---

## 8. Settings (Inside Profile Popup)

All settings are inside the profile popup. There is no separate settings page.

**Covered in profile popup:**
- Profile info
- Security (password, 2FA)
- Preferences (theme, language, timezone)
- Billing
- Danger zone (delete account)

---

## 9. Notifications

Accessible from the bell icon in the top bar.

**Types:**
- Success — file ready, payment successful
- Warning — storage at 80%, approaching thread limit
- Error — file processing failed, payment failed
- Info — new team member joined, MCP connection made

**Actions:**
- Mark all as read
- Click notification → goes to relevant page
- Dismiss individual notification

---

## 10. Error States and Empty States

### Empty States

| Screen | Empty State Message |
|---|---|
| Dashboard (no buckets) | "Create your first bucket to get started." |
| Bucket (no files) | "Upload your first file to start chatting with your bucket." |
| Bucket (no conversations) | "Start a new conversation to chat with your documents." |
| Notifications (none) | "You are all caught up." |

### Error States

| Error | Message Shown |
|---|---|
| File processing failed | "We had trouble processing this file. Please try uploading it again." |
| Payment failed | "Your payment could not be processed. Please update your billing details." |
| Storage limit reached | "You have reached your storage limit. Please upgrade your plan." |
| Thread limit reached | "You have reached the maximum of 20 conversation threads for this bucket. Delete an old thread to start a new one." |
| Network error | "Something went wrong. Please check your connection and try again." |

---

## 11. Legal Pages

### Privacy Policy Page
- Full privacy policy text
- Last updated date

### Terms of Service Page
- Full terms of service text
- Last updated date

### Tokushoho Page (特定商取引法に基づく表記)
- Required in Japan for Stripe payments
- Business name, address, contact, pricing, refund policy

---

## 12. 404 Page

Shown when user visits a page that does not exist.

- Clean message: "This page does not exist."
- Button: "Go back to Dashboard"

---

## Full User Journey Map

```
New User
        |
        v
Landing Page
        |
        v
Signup → Email Verification → Onboarding → Dashboard
                                                |
                        +-----------------------+
                        |
                 Create Bucket
                        |
                 Bucket Page
                        |
              +—————————+—————————+
              |                   |
         Upload Files         Start Conversation Thread
              |                   |
         Doc Page            Send Unlimited Messages
              |                   |
         View Summary        Get AI Answer + Sources
              |
         Copy MCP URL
              |
         Paste into Claude / ChatGPT
              |
         External AI queries bucket in real time

Returning User
        |
        v
Login → (2FA if enabled) → Dashboard → Bucket → Chat
```

---

*Document version: 1.1 — March 2026 — Updated conversation limit clarification*
