# User Guides - AIveilix

Complete step-by-step guides to help you get started and make the most of AIveilix.

---

## Quick Start

Get up and running with AIveilix in minutes. This guide walks you through everything from creating your account to chatting with your documents.

### Step 1: Create Your Account



1. Navigate to the signup page
2. You'll see a glassmorphic card with the heading **"Create Account"**
3. Fill in the required fields:
   - **Full Name** field with user icon
   - **Email** field (must be valid email format like `you@example.com`)
   - **Password** field (minimum 6 characters)
   - **Confirm Password** field (must match your password)
4. Check the **"By creating an account, you agree to our Terms and Conditions and Privacy Policy"** checkbox
5. Click the **"Create Account"** button (teal/accent colored)

**What Happens Next:**
- A success message appears in a green box: *"Account created! Please check your email to verify."*
- Check your email inbox for a verification email from AIveilix
- Click the verification link to activate your account

**Validation:**
- Name is required
- Email must be in valid format (`user@domain.com`)
- Password minimum 6 characters
- Passwords must match
- Terms checkbox must be checked (button disabled until checked)


**Helpful Links:**
- Already have an account? Click **"Sign in"** link at the bottom
- Can navigate to **Terms and Conditions** and **Privacy Policy** (opens in new tab)

---

### Step 2: Login to Your Account



1. Navigate to the login page
2. You'll see a glass card with **"Welcome Back"** heading
3. Enter your credentials:
   - **Email** field with envelope icon
   - **Password** field with lock icon (password hidden with bullets •••)
4. Click **"Sign In"** button (teal accent color)

**Features:**
- **Forgot password?** link in top-right of form
- Error messages appear in red box if credentials are wrong
- Loading spinner appears on button while authenticating

**After Successful Login:**
- Automatically redirected to `/dashboard`
- Login notification created in your notifications panel
- Session tokens stored securely in browser localStorage

**Troubleshooting:**
- **"Login failed"** error: Double-check email and password
- **Account not verified**: Check your email for verification link
- **Forgot password**: Click the "Forgot password?" link


---

### Step 3: Password Recovery (Optional)



**If you forgot your password:**

1. Click **"Forgot password?"** link on login page
2. See heading: **"Forgot Password?"** with subtitle *"No worries, we'll send you reset instructions."*
3. Enter your **Email** address
4. Click **"Send Reset Link"** button
5. Success screen appears with:
   - Envelope icon in teal circle
   - **"Check Your Email"** heading
   - Message showing your email address
   - **"Back to Login"** button


**Email Instructions:**
- Check your inbox for password reset email
- Click the reset link (valid for limited time)
- Set your new password
- Return to login page

---

### Step 4: Dashboard Overview



**After logging in, you'll see:**

**Header Bar (Top):**
- **AIveilix** logo (teal/accent color)
- **"Welcome, [Your Name]"** greeting
- Right side controls:
  - **Notification icon** (bell icon with unread count badge)
  - **Profile icon** (user avatar circle)
  - **Theme toggle** (sun/moon icon)

**Main Dashboard Sections:**

**1. Create Bucket Button (Top Right)**
- Large **"Create New Bucket"** button (teal accent)
- Maximum width 200px, prominent placement


**2. Statistics Cards (3 Cards in Row)**


| Stat Card | Icon | Description |
|-----------|------|-------------|
| **Total Buckets** | Cube icon | Shows total number of knowledge vaults |
| **Total Files** | Document icon | Shows total uploaded documents |
| **Total Storage** | Database icon | Shows storage used (e.g., "245.67 MB") |

- Glass morphism cards with icons
- Real-time data from your account
- Automatic updates when you create/delete items

**3. Activity Graph**


- **DashboardGraph** component with Recharts LineChart
- Shows cumulative growth of:
  - Files (green line)
  - Buckets (blue line)
  - Storage (purple line)
- **Date range picker** to filter activity (last 7/30/90 days)
- Hover over points to see exact values
- Responsive design adapts to screen size

**4. Buckets Table**


- **"Your Buckets"** heading
- Table columns:
  - **Name**: Bucket title with description
  - **Files**: Number of files in bucket
  - **Size**: Total storage used
  - **Created**: Date created
  - **Actions**: View and Delete buttons

- Each row is clickable to open the bucket
- **Delete button** appears on hover (red trash icon)
- Empty state: "No buckets yet. Create your first bucket above!"

---

### Step 5: Create Your First Bucket



1. Click **"Create New Bucket"** button from dashboard
2. Modal appears with heading **"Create New Bucket"**
3. Modal has **2-column layout**:

**Left Column - Bucket Details:**


**Heading:** "Bucket Details"

- **Bucket Name** field
  - Placeholder: "My Knowledge Bucket"
  - Required field
  - Example: "Work Projects", "Personal Notes", "Research Papers"

- **Description** field (optional)
  - Multiline textarea (4 rows)
  - Placeholder: "What's in this bucket?"
  - Example: "All my work-related documents and code"
  - Supports up to ~500 characters

- **Create Bucket** button (full width, teal accent)
  - Shows loading spinner while creating
  - Disabled if name is empty

**Right Column - Upload Files (Optional):**


**Heading:** "Upload Files (Optional)"

**Dashed border upload zone** with two options:

**Option 1: Upload Files**
- Cloud upload icon (teal)
- **"Click to upload files"** text
- "Any file type" subtitle
- Click to open file browser
- Select multiple files at once

**OR divider** (horizontal line with "OR" text)

**Option 2: Upload Folder**
- Folder icon (teal)
- **"Click to upload folder"** text
- "Upload entire folder with all files" subtitle
- Click to open folder browser
- Preserves folder structure


**After Selecting Files:**

**Selected Files List** appears showing:
- File icon or folder icon
- File name (truncated if long)
- Folder path (if from folder upload)
- File size (e.g., "2.5 KB")
- Red X button to remove file


**Example File Entry:**
```
📄 document.pdf
   2.5 MB
[X] (delete button on hover)
```

**Example Folder File Entry:**
```
📁 project/docs/readme.md
   project/docs
   1.2 KB
[X]
```

**Supported File Types:**
- **Documents:** PDF, DOCX, TXT, RTF, ODT
- **Images:** JPG, PNG, GIF, BMP, WebP, TIFF
- **Code:** Python, JavaScript, TypeScript, Java, C++, Go, Rust, etc. (50+ languages)
- **Data:** CSV, JSON, XML, YAML
- **Markdown:** MD, MDX

**Upload Process:**
1. Select files/folder
2. Files appear in "Selected Files" list
3. Click **"Create Bucket"** button
4. Bucket is created first
5. Files upload one by one (async)
6. Processing status shown for each file
7. Modal closes on completion
8. Dashboard refreshes with new bucket

**Note:** You can skip file upload and add files later from the bucket page.

---

### Step 6: Bucket Workflow


Watch the animated demonstration below to see the complete bucket workflow:

- Opening and viewing your bucket
- Uploading files to your bucket
- Selecting files for AI chat context
- Chatting with your documents
- AI analyzing and responding with sources
- Creating new conversations
- Using web search integration

**The GIF below shows each feature step-by-step.**


### Step 7: Profile & Settings


Access your profile settings via the profile icon in the top-right header. The Profile Settings modal has 3 tabs:

- **Profile:** Avatar, personal info, change password, theme toggle, danger zone
- **Credentials:** API Keys and OAuth Clients for external integrations
- **Subscription:** Current plan, usage meters, billing management

**The GIF below demonstrates all features step-by-step.**

---
