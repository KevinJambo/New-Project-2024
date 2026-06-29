# OneDrive Audit & Organization Tool

A comprehensive Python tool for auditing, managing, and organizing OneDrive folders with advanced duplicate detection, folder organization, and reporting capabilities.

## 🎯 Features

- **📊 Folder Scanning**: Recursively scan entire OneDrive structure and collect file metadata
- **🔍 Duplicate Detection**: Find duplicate files using SHA-256 content hashing
- **🗑️ Duplicate Removal**: Remove duplicates with configurable retention strategies (oldest/newest)
- **📁 File Organization**: 
  - Organize by file type (extension)
  - Organize by modification date (year/month)
  - Create custom folder structures
- **📈 Detailed Reports**: Generate comprehensive audit reports with metrics and statistics
- **🔐 Secure Authentication**: OAuth 2.0 with Microsoft Graph API
- **📝 Logging & Tracking**: Track all operations with confirmation prompts

## 📋 Requirements

- Python 3.8 or higher
- Microsoft 365 account with OneDrive
- Azure App Registration with appropriate permissions

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repo>
cd New-Project-2024
pip install -r requirements.txt
```

### 2. Create Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com/)
2. **Azure Active Directory** → **App registrations** → **New registration**
3. Set application name and redirect URI: `http://localhost`
4. Copy the **Application (client) ID**
5. Go to **API permissions** and add:
   - `Files.ReadWrite.All` (Delegated)
   - `offline_access` (Delegated)
6. Grant admin consent

### 3. Configure Environment

Create `.env` file:
```
ONEDRIVE_CLIENT_ID=your_client_id_here
```

Or set environment variable:
```bash
export ONEDRIVE_CLIENT_ID=your_client_id
```

### 4. Run the Tool

```bash
# Interactive mode
python onedrive_audit.py

# Command-line mode with full audit
python cli.py --full-audit

# Run examples
python examples.py
```

## 💻 Usage

### Command Line Interface

```bash
# Scan OneDrive
python cli.py --scan

# Find duplicates
python cli.py --scan --find-duplicates

# Remove duplicates (keep oldest)
python cli.py --remove-duplicates --keep-strategy oldest

# Organize by file type
python cli.py --organize type

# Organize by date
python cli.py --organize date

# Complete workflow
python cli.py --full-audit

# Create custom folder structure
python cli.py --create-structure example_folder_structure.json

# Generate report
python cli.py --report my_audit_report.json
```

### Python API

```python
from onedrive_audit import OneDriveAuditor

# Initialize
auditor = OneDriveAuditor("your_client_id")
auditor.authenticate()

# Get root folder
root_id = auditor.get_drive_root()

# Scan folders
files = auditor.scan_folder(root_id)

# Find duplicates
duplicates = auditor.find_duplicates(files)

# Remove duplicates
auditor.remove_duplicates(duplicates, keep_strategy="oldest")

# Organize files
auditor.organize_by_type(root_id, files)

# Generate report
auditor.generate_audit_report("report.json")
```

## 📊 Audit Report

The generated `audit_report.json` includes:

```json
{
  "total_files": 5000,
  "total_size": 107374182400,
  "duplicates_found": 42,
  "duplicates_removed": 42,
  "files_organized": 4958,
  "new_folders_created": 8,
  "timestamp": "2024-06-29T12:34:56.789123"
}
```

## 📂 Folder Structure Templates

Use `example_folder_structure.json` as a template for custom organizations:

```json
{
  "Documents": {
    "Work": {},
    "Personal": {},
    "Financial": {}
  },
  "Media": {
    "Photos": {},
    "Videos": {}
  }
}
```

## 🔧 Advanced Configuration

### Custom Keep Strategy

```python
# Keep newest versions
auditor.remove_duplicates(duplicates, keep_strategy="newest")

# Keep oldest versions (default)
auditor.remove_duplicates(duplicates, keep_strategy="oldest")
```

### Manual File Operations

```python
# Move file to folder
auditor.move_file(file_id, new_parent_id)

# Delete file
auditor.delete_file(file_id)

# Calculate file hash
file_hash = auditor.calculate_file_hash(file_id)
```

## 📖 Examples

Run the interactive examples:

```bash
python examples.py
```

Available examples:
1. Basic folder scan
2. Find duplicate files
3. Remove duplicates
4. Organize by file type
5. Organize by date
6. Create custom folder structure
7. Complete audit workflow
8. Generate detailed report

## 🔐 Security

- **OAuth 2.0**: Secure authentication with device flow
- **No Password Storage**: Credentials managed by OS token store
- **Direct API**: All requests go directly to Microsoft Graph
- **Content Hashing**: SHA-256 for accurate duplicate detection
- **Delegated Permissions**: Only necessary permissions requested

## ⚠️ Safety Features

- Content-based duplicate detection (not filename matching)
- Original file always preserved; only duplicates removed
- Configurable retention strategies
- All operations logged with confirmation
- Token caching for improved performance

## 🆘 Troubleshooting

**Authentication fails**
- Verify Azure app registration
- Check `Files.ReadWrite.All` permission is granted
- Delete `.msal_token_cache.bin` to clear cache

**Large folders take too long**
- Normal for 10,000+ files
- Can interrupt with Ctrl+C and resume later
- Large file hashing requires time

**Permission errors**
- Ensure delegated (not application) permissions
- Grant admin consent for API permissions
- Verify user has OneDrive access

## 📝 Logging

Operations are logged to console with:
- ✓ Success indicators
- ✗ Error indicators
- Progress counters for long operations

## 🤝 Contributing

Improvements welcome! Key areas:
- Performance optimization for large OneDrive folders
- Additional organization strategies
- Enhanced reporting and analytics
- Multi-folder support

## 📄 License

MIT License - See LICENSE file for details
