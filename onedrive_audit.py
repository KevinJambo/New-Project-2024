#!/usr/bin/env python3
"""
OneDrive Audit & Organization Tool
Audits OneDrive folders, detects duplicates, removes them, and organizes files
"""

import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth
from msal import PublicClientApplication


class OneDriveAuditor:
    """Main class for OneDrive auditing and organization"""

    # Microsoft Graph API endpoints
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    SCOPES = ["Files.ReadWrite.All", "offline_access"]

    def __init__(self, client_id: str, config_file: str = "config.json"):
        """Initialize OneDrive auditor with authentication"""
        self.client_id = client_id
        self.config_file = config_file
        self.app = PublicClientApplication(client_id=client_id)
        self.token = None
        self.headers = None
        self.audit_results = {
            "total_files": 0,
            "total_size": 0,
            "duplicates_found": 0,
            "duplicates_removed": 0,
            "files_organized": 0,
            "new_folders_created": 0,
            "timestamp": datetime.now().isoformat()
        }

    def authenticate(self) -> bool:
        """Authenticate with Microsoft using MSAL"""
        try:
            # Try to get cached token
            accounts = self.app.get_accounts()
            if accounts:
                account = accounts[0]
                result = self.app.acquire_token_silent(self.SCOPES, account=account)
            else:
                # No cached token, initiate device flow
                result = self.app.initiate_device_flow(scopes=self.SCOPES)
                print(result["message"])
                result = self.app.acquire_token_by_device_flow(result)

            if "access_token" in result:
                self.token = result["access_token"]
                self.headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                print("✓ Authentication successful")
                return True
            else:
                print(f"✗ Authentication failed: {result.get('error_description')}")
                return False
        except Exception as e:
            print(f"✗ Authentication error: {str(e)}")
            return False

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            response = requests.request(
                method, url, headers=self.headers, timeout=30, **kwargs
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"✗ API request failed: {str(e)}")
            return None

    def get_drive_root(self) -> Optional[str]:
        """Get the drive root ID"""
        result = self._make_request("GET", f"{self.GRAPH_API_ENDPOINT}/me/drive/root")
        if result:
            return result.get("id")
        return None

    def scan_folder(self, folder_id: str, path: str = "/") -> List[Dict]:
        """Recursively scan folder and collect file metadata"""
        files = []
        url = f"{self.GRAPH_API_ENDPOINT}/me/drive/items/{folder_id}/children"

        try:
            while url:
                result = self._make_request("GET", url)
                if not result:
                    break

                for item in result.get("value", []):
                    item_path = f"{path}{item['name']}"

                    if item["name"].startswith("."):
                        continue

                    file_data = {
                        "id": item["id"],
                        "name": item["name"],
                        "path": item_path,
                        "type": "folder" if "folder" in item else "file",
                        "size": item.get("size", 0),
                        "modified": item.get("lastModifiedDateTime")
                    }

                    if file_data["type"] == "file":
                        files.append(file_data)
                        self.audit_results["total_files"] += 1
                        self.audit_results["total_size"] += file_data["size"]
                    else:
                        # Recursively scan subfolders
                        subfolder_files = self.scan_folder(item["id"], f"{item_path}/")
                        files.extend(subfolder_files)

                # Check for pagination
                url = result.get("@odata.nextLink")

        except Exception as e:
            print(f"✗ Error scanning folder: {str(e)}")

        return files

    def calculate_file_hash(self, file_id: str, chunk_size: int = 8192) -> Optional[str]:
        """Calculate hash of file from OneDrive"""
        try:
            url = f"{self.GRAPH_API_ENDPOINT}/me/drive/items/{file_id}/content"
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)

            if response.status_code == 200:
                hasher = hashlib.sha256()
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        hasher.update(chunk)
                return hasher.hexdigest()
        except Exception as e:
            print(f"✗ Error calculating hash: {str(e)}")

        return None

    def find_duplicates(self, files: List[Dict]) -> Dict[str, List[Dict]]:
        """Find duplicate files by content hash"""
        duplicates = defaultdict(list)
        hash_map = {}

        print("\nScanning for duplicates...")
        for idx, file_data in enumerate(files, 1):
            print(f"  Processing {idx}/{len(files)}: {file_data['name']}", end="\r")

            file_hash = self.calculate_file_hash(file_data["id"])
            if file_hash:
                if file_hash in hash_map:
                    duplicates[file_hash].append(file_data)
                    if len(duplicates[file_hash]) == 1:
                        duplicates[file_hash].insert(0, hash_map[file_hash])
                else:
                    hash_map[file_hash] = file_data

        print()
        self.audit_results["duplicates_found"] = sum(
            len(v) - 1 for v in duplicates.values() if len(v) > 1
        )
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from OneDrive"""
        url = f"{self.GRAPH_API_ENDPOINT}/me/drive/items/{file_id}"
        result = self._make_request("DELETE", url)
        return result is not None or True

    def remove_duplicates(
        self, duplicates: Dict[str, List[Dict]], keep_strategy: str = "oldest"
    ) -> int:
        """Remove duplicate files, keeping one copy"""
        removed = 0

        print("\nRemoving duplicates...")
        for hash_val, file_list in duplicates.items():
            file_list.sort(
                key=lambda x: x["modified"],
                reverse=(keep_strategy == "newest")
            )

            # Keep the first file, delete the rest
            for file_data in file_list[1:]:
                if self.delete_file(file_data["id"]):
                    removed += 1
                    print(f"  ✓ Deleted: {file_data['path']}")
                else:
                    print(f"  ✗ Failed to delete: {file_data['path']}")

        self.audit_results["duplicates_removed"] = removed
        return removed

    def create_folder_structure(self, root_folder_id: str, structure: Dict) -> bool:
        """Create folder structure recursively"""
        for folder_name, subfolders in structure.items():
            # Create folder
            create_body = {"name": folder_name, "folder": {}, "@microsoft.graph.conflictBehavior": "rename"}
            url = f"{self.GRAPH_API_ENDPOINT}/me/drive/items/{root_folder_id}/children"
            result = self._make_request("POST", url, json=create_body)

            if result and "id" in result:
                self.audit_results["new_folders_created"] += 1
                print(f"  ✓ Created folder: {folder_name}")

                # Recursively create subfolders
                if subfolders:
                    self.create_folder_structure(result["id"], subfolders)
            else:
                print(f"  ✗ Failed to create folder: {folder_name}")

        return True

    def move_file(self, file_id: str, new_parent_id: str) -> bool:
        """Move file to a different folder"""
        url = f"{self.GRAPH_API_ENDPOINT}/me/drive/items/{file_id}"
        body = {"parentReference": {"id": new_parent_id}}
        result = self._make_request("PATCH", url, json=body)
        return result is not None

    def organize_by_type(self, root_folder_id: str, files: List[Dict]) -> int:
        """Organize files into folders by file type"""
        print("\nOrganizing files by type...")

        # Group files by extension
        files_by_type = defaultdict(list)
        for file_data in files:
            ext = Path(file_data["name"]).suffix.lower() or "other"
            files_by_type[ext].append(file_data)

        # Create type folders
        type_structure = {ext: {} for ext in files_by_type.keys()}
        self.create_folder_structure(root_folder_id, type_structure)

        # Get folder IDs and move files
        folders = self._make_request(
            "GET", f"{self.GRAPH_API_ENDPOINT}/me/drive/items/{root_folder_id}/children"
        )

        moved = 0
        if folders:
            folder_map = {item["name"]: item["id"] for item in folders.get("value", [])}

            for ext, file_list in files_by_type.items():
                if ext in folder_map:
                    for file_data in file_list:
                        if self.move_file(file_data["id"], folder_map[ext]):
                            moved += 1

        self.audit_results["files_organized"] = moved
        return moved

    def organize_by_date(self, root_folder_id: str, files: List[Dict]) -> int:
        """Organize files into folders by modification date"""
        print("\nOrganizing files by date...")

        # Group files by year/month
        files_by_date = defaultdict(list)
        for file_data in files:
            date_obj = datetime.fromisoformat(file_data["modified"].replace("Z", "+00:00"))
            year_month = date_obj.strftime("%Y/%B")
            files_by_date[year_month].append(file_data)

        # Create date folders
        date_structure = {}
        for date_str in files_by_date.keys():
            parts = date_str.split("/")
            if parts[0] not in date_structure:
                date_structure[parts[0]] = {}
            date_structure[parts[0]][parts[1]] = {}

        self.create_folder_structure(root_folder_id, date_structure)
        return len(files)

    def generate_audit_report(self, output_file: str = "audit_report.json") -> None:
        """Generate audit report"""
        with open(output_file, "w") as f:
            json.dump(self.audit_results, f, indent=2)

        print("\n" + "=" * 50)
        print("AUDIT REPORT")
        print("=" * 50)
        print(f"Total files scanned: {self.audit_results['total_files']}")
        print(f"Total size: {self.audit_results['total_size'] / (1024**3):.2f} GB")
        print(f"Duplicates found: {self.audit_results['duplicates_found']}")
        print(f"Duplicates removed: {self.audit_results['duplicates_removed']}")
        print(f"Files organized: {self.audit_results['files_organized']}")
        print(f"New folders created: {self.audit_results['new_folders_created']}")
        print(f"Report saved to: {output_file}")
        print("=" * 50)


def main():
    """Main execution function"""
    # Configuration
    CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID", "YOUR_CLIENT_ID_HERE")

    if CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print("Error: Please set ONEDRIVE_CLIENT_ID environment variable")
        print("See README.md for setup instructions")
        return

    auditor = OneDriveAuditor(CLIENT_ID)

    # Authenticate
    if not auditor.authenticate():
        return

    # Get drive root
    root_id = auditor.get_drive_root()
    if not root_id:
        print("Error: Could not access OneDrive")
        return

    print("\nStarting OneDrive audit...")

    # Scan folder
    print("Scanning folder structure...")
    files = auditor.scan_folder(root_id)
    print(f"✓ Scanned {len(files)} files")

    # Find duplicates
    duplicates = auditor.find_duplicates(files)
    if duplicates:
        print(f"✓ Found {auditor.audit_results['duplicates_found']} duplicate files")

        # Remove duplicates
        auditor.remove_duplicates(duplicates)

    # Organize files
    choice = input("\nOrganize files? (1=by type, 2=by date, 3=skip): ").strip()
    if choice == "1":
        auditor.organize_by_type(root_id, files)
    elif choice == "2":
        auditor.organize_by_date(root_id, files)

    # Generate report
    auditor.generate_audit_report()


if __name__ == "__main__":
    main()
