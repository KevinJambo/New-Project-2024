# VOV File Organization Workflow

Complete guide to cleaning up and organizing VOV files.

## 📋 Overview

Two-step process:
1. **Extract ZIPs** → Clean up ZIP archives
2. **Organize Files** → Sort everything into categories

---

## Step 1: Extract ZIP Files

### What It Does
- Finds all `.zip` files in a folder
- Shows you what's inside
- Extracts files (safe preview first)
- Optionally deletes ZIPs to free space

### Usage

**Preview (see what will happen, no changes):**
```bash
python zip_cleaner.py "C:\path\to\zip\folder"
```

**Actually extract files:**
```bash
python zip_cleaner.py "C:\path\to\zip\folder" --extract
```

**Extract AND delete original ZIPs:**
```bash
python zip_cleaner.py "C:\path\to\zip\folder" --extract --delete
```

**Extract to subfolders instead of same folder:**
```bash
python zip_cleaner.py "C:\path\to\zip\folder" --extract --subfolder
```

### Output
- Console shows: ZIPs found, files inside, results
- Report saved: `zip_extraction_report.json`

---

## Step 2: Organize Files

### What It Does
- Scans folder for all files
- Categorizes by type:
  - **Sheet Music/** → PDF, MusicXML, Sibelius files
  - **Videos/** → MP4, AVI, MOV, WebM, etc.
  - **Pictures/** → JPG, PNG, GIF, TIFF, etc.
  - **Audio/** → MP3, WAV, FLAC, AAC, etc.
  - **Documents/** → Word, Excel, PowerPoint, etc.
  - **Other/** → Anything else
- Moves files into folders
- Generates report

### Usage

**Preview (see organization plan, no changes):**
```bash
python vov_organizer.py "C:\path\to\organize"
```

**Actually organize files:**
```bash
python vov_organizer.py "C:\path\to\organize" --execute
```

**Custom report name:**
```bash
python vov_organizer.py "C:\path\to\organize" --execute --report my_report.json
```

### Output
- Console shows: Files found, organization plan, results
- Report saved: `organization_report.json` (or custom name)

---

## 🔄 Complete Workflow Example

Here's the full process:

### Scenario: Clean up ZIPs in OneDrive VOV folder

**Step 1: Find the path**
```
C:\Users\YourName\OneDrive - Voices of Vets
```

**Step 2: Preview ZIP extraction**
```bash
python zip_cleaner.py "C:\Users\YourName\OneDrive - Voices of Vets"
```

Review output. If it looks good, extract:
```bash
python zip_cleaner.py "C:\Users\YourName\OneDrive - Voices of Vets" --extract --delete
```

**Step 3: Preview file organization**
```bash
python vov_organizer.py "C:\Users\YourName\OneDrive - Voices of Vets"
```

Review output. If it looks good, organize:
```bash
python vov_organizer.py "C:\Users\YourName\OneDrive - Voices of Vets" --execute
```

**Step 4: Check reports**
- `zip_extraction_report.json` - What was extracted
- `organization_report.json` - What was organized

---

## 🛡️ Safety Tips

1. **Always do DRY RUN first** (no `--execute` or `--extract`)
2. **Review the output** before running with flags
3. **Check reports** after each step
4. **Keep backups** of important files
5. **Test with small folder first** before running on entire VOV folder

---

## 📊 Report Files

### `zip_extraction_report.json`
```json
{
  "total_zips": 5,
  "successfully_extracted": 5,
  "failed_extractions": 0,
  "total_files_extracted": 247,
  "space_freed_bytes": 1073741824,
  "zips_deleted": 5
}
```

### `organization_report.json`
```json
{
  "total_files": 350,
  "organized_files": 340,
  "skipped_files": 10,
  "new_folders_created": 6,
  "files_by_category": {
    "Sheet Music": 125,
    "Videos": 45,
    "Pictures": 78,
    "Audio": 92,
    "Other": 10
  }
}
```

---

## 🆘 Troubleshooting

### "Permission denied" error
- Make sure you have read/write access to the folder
- Close the folder in File Explorer before running
- Run command prompt as Administrator

### "File already exists" warning
- Script skips duplicates (won't overwrite)
- Check `organization_report.json` for skipped files
- Manually resolve duplicates if needed

### ZIP extraction fails
- Check if ZIP file is corrupted: try opening in Explorer
- Check disk space
- Try with `--subfolder` flag

### Files not moving
- Check if files are locked (open in another program)
- Check file permissions
- Review errors in report

---

## 📝 Next Steps

After organizing:

1. **Review folder structure** in File Explorer
2. **Verify reports** for any issues
3. **Check "Other" folder** for misclassified files
4. **Adjust if needed** by manually moving files
5. **Keep reports** as reference

---

## ⚙️ Customization

Want to change file categories? Edit the script:
- Open `vov_organizer.py`
- Find `CATEGORIES` dictionary (around line 19)
- Add/remove file extensions
- Save and run again

Example: Add XML files to Sheet Music
```python
"Sheet Music": [".pdf", ".musicxml", ".xml", ".mus", ".sib", ".musx", ".xml"],
```

---

## 💡 Tips

- Run scripts from Project folder (where both `.py` files are)
- Use full paths in quotes: `"C:\path\to\folder"`
- Reports help track what changed
- Can run multiple times (organizer skips already-organized files)
- Best run during off-peak hours if OneDrive is syncing
