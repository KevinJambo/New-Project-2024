# OneDrive Audit & Organization Tool - Setup Guide

## Overview
This tool audits your OneDrive folder, finds and removes duplicates, creates organized folder structures, and generates a detailed report.

## Features
- ✓ Scan entire OneDrive folder structure
- ✓ Detect duplicate files using SHA-256 hashing
- ✓ Remove duplicates (keeps oldest or newest)
- ✓ Organize files by file type (extension)
- ✓ Organize files by date (year/month)
- ✓ Generate audit reports
- ✓ Track storage and optimization metrics

## Prerequisites
- Python 3.8+
- Microsoft 365 account with OneDrive
- Azure App Registration

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Register Azure App

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Set up the app:
   - **Name**: OneDrive Audit Tool
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: http://localhost (or leave empty)
   - Click **Register**

4. Copy the **Application (client) ID** from the Overview page

5. Go to **API permissions**:
   - Click **Add a permission**
   - Select **Microsoft Graph**
   - Select **Delegated permissions**
   - Search and add:
     - `Files.ReadWrite.All`
     - `offline_access`
   - Click **Grant admin consent**

### 3. Configure Environment

Create a `.env` file in the project root:
```
ONEDRIVE_CLIENT_ID=your_client_id_here
```

Or set the environment variable:
```bash
export ONEDRIVE_CLIENT_ID=your_client_id
```

### 4. Run the Tool

```bash
python onedrive_audit.py
```

## First Run

1. The tool will prompt you with a device login code
2. Visit https://microsoft.com/devicelogin
3. Enter the code provided
4. Sign in with your Microsoft 365 account
5. Grant permissions when prompted
6. The tool begins scanning

## Usage Examples

### Scan and find duplicates
```bash
python onedrive_audit.py
# Select option when prompted to organize files
```

### Advanced Usage

```python
from onedrive_audit import OneDriveAuditor

auditor = OneDriveAuditor("your_client_id")
auditor.authenticate()
root_id = auditor.get_drive_root()

# Scan
files = auditor.scan_folder(root_id)

# Find duplicates
duplicates = auditor.find_duplicates(files)

# Remove duplicates (keep oldest)
auditor.remove_duplicates(duplicates, keep_strategy="oldest")

# Organize by type
auditor.organize_by_type(root_id, files)

# Generate report
auditor.generate_audit_report("my_report.json")
```

## Output

After running, you'll get:
- **audit_report.json** - Detailed metrics and results
- Console output with progress and summary

## Report Metrics

- `total_files`: Number of files scanned
- `total_size`: Total storage used (in bytes)
- `duplicates_found`: Number of duplicate files detected
- `duplicates_removed`: Number of duplicates deleted
- `files_organized`: Number of files moved to organized folders
- `new_folders_created`: Number of new folders created
- `timestamp`: When the audit was run

## Safety Features

- Duplicates are identified by content hash (SHA-256), not filename
- Original file is kept; only duplicates are removed
- Supports "oldest" and "newest" retention strategies
- All operations are logged with confirmation prompts
- Token is cached securely in system token store

## Troubleshooting

### Authentication fails
- Ensure Azure app is registered correctly
- Check that `Files.ReadWrite.All` permission is granted
- Clear cached token: delete `.msal_token_cache.bin` file

### Large folder takes too long
- Tool processes files sequentially by design
- Large OneDrive folders (>10,000 files) may take hours
- You can interrupt (Ctrl+C) and resume later

### Hash calculation is slow
- Large files require more time to hash
- This is normal and necessary for accurate duplicate detection

### Permission errors
- Ensure app has delegated permissions (not application)
- Grant admin consent for `Files.ReadWrite.All`

## Security Notes

- This tool uses OAuth 2.0 with device flow authentication
- Tokens are stored securely by the OS
- The tool never stores your password
- All API calls go directly to Microsoft Graph API

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Azure app permissions
3. Ensure Microsoft Graph API access is enabled
