#!/usr/bin/env python3
"""
Command-line interface for OneDrive Audit & Organization Tool
"""

import argparse
import sys
import json
from pathlib import Path
from onedrive_audit import OneDriveAuditor


class OneDriveCLI:
    """CLI interface for OneDrive auditor"""

    def __init__(self):
        self.auditor = None

    def parse_args(self):
        """Parse command-line arguments"""
        parser = argparse.ArgumentParser(
            description="OneDrive Audit & Organization Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python cli.py --scan                    # Scan OneDrive
  python cli.py --scan --find-duplicates  # Scan and find duplicates
  python cli.py --remove-duplicates       # Remove found duplicates
  python cli.py --organize type           # Organize by file type
  python cli.py --organize date           # Organize by date
  python cli.py --full-audit              # Complete audit workflow
  python cli.py --report report.json      # Generate report
            """
        )

        parser.add_argument(
            "--client-id",
            help="Microsoft Graph API Client ID (or set ONEDRIVE_CLIENT_ID env var)",
            default=None
        )

        parser.add_argument(
            "--scan",
            action="store_true",
            help="Scan OneDrive folder structure"
        )

        parser.add_argument(
            "--find-duplicates",
            action="store_true",
            help="Find duplicate files"
        )

        parser.add_argument(
            "--remove-duplicates",
            action="store_true",
            help="Remove duplicate files"
        )

        parser.add_argument(
            "--keep-strategy",
            choices=["oldest", "newest"],
            default="oldest",
            help="Strategy for keeping files when removing duplicates"
        )

        parser.add_argument(
            "--organize",
            choices=["type", "date"],
            help="Organize files by type or date"
        )

        parser.add_argument(
            "--create-structure",
            type=str,
            help="Create folder structure from JSON file"
        )

        parser.add_argument(
            "--report",
            type=str,
            default="audit_report.json",
            help="Output report filename"
        )

        parser.add_argument(
            "--full-audit",
            action="store_true",
            help="Run complete audit workflow (scan, find, remove, organize)"
        )

        parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Verbose output"
        )

        return parser.parse_args()

    def authenticate(self, client_id):
        """Initialize and authenticate"""
        if not client_id:
            import os
            client_id = os.getenv("ONEDRIVE_CLIENT_ID")

        if not client_id:
            print("Error: Client ID required. Set ONEDRIVE_CLIENT_ID or use --client-id")
            sys.exit(1)

        self.auditor = OneDriveAuditor(client_id)
        if not self.auditor.authenticate():
            print("Authentication failed")
            sys.exit(1)

        return self.auditor.get_drive_root()

    def load_folder_structure(self, json_file):
        """Load folder structure from JSON file"""
        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File {json_file} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {json_file}")
            sys.exit(1)

    def run_full_audit(self, root_id):
        """Run complete audit workflow"""
        print("\n" + "=" * 60)
        print("RUNNING FULL ONEDRIVE AUDIT")
        print("=" * 60)

        # Scan
        print("\n[1/4] Scanning OneDrive...")
        files = self.auditor.scan_folder(root_id)
        print(f"✓ Scanned {len(files)} files")

        # Find duplicates
        print("\n[2/4] Finding duplicates...")
        duplicates = self.auditor.find_duplicates(files)
        if duplicates:
            print(f"✓ Found {self.auditor.audit_results['duplicates_found']} duplicates")

            # Remove duplicates
            print("\n[3/4] Removing duplicates...")
            self.auditor.remove_duplicates(duplicates, keep_strategy="oldest")
            print(f"✓ Removed {self.auditor.audit_results['duplicates_removed']} files")
        else:
            print("✓ No duplicates found")

        # Organize
        print("\n[4/4] Organizing files by type...")
        self.auditor.organize_by_type(root_id, files)
        print(f"✓ Organized {self.auditor.audit_results['files_organized']} files")

        print("\n" + "=" * 60)
        print("AUDIT COMPLETE")
        print("=" * 60)

    def main(self):
        """Main CLI execution"""
        args = self.parse_args()

        # Authenticate
        root_id = self.authenticate(args.client_id)
        if not root_id:
            print("Error: Could not access OneDrive root")
            sys.exit(1)

        # Handle full audit first
        if args.full_audit:
            self.run_full_audit(root_id)
            self.auditor.generate_audit_report(args.report)
            return

        # Handle individual commands
        files = None

        if args.scan or args.find_duplicates or args.remove_duplicates or args.organize:
            print("Scanning OneDrive...")
            files = self.auditor.scan_folder(root_id)
            if args.scan:
                print(f"✓ Scanned {len(files)} files")
                print(f"  Total size: {self.auditor.audit_results['total_size'] / (1024**3):.2f} GB")

        if args.find_duplicates and files:
            print("Finding duplicates...")
            duplicates = self.auditor.find_duplicates(files)
            if duplicates:
                print(f"✓ Found {self.auditor.audit_results['duplicates_found']} duplicates")
            else:
                print("✓ No duplicates found")

        if args.remove_duplicates and files:
            duplicates = self.auditor.find_duplicates(files)
            if duplicates:
                print(f"Removing duplicates (keep strategy: {args.keep_strategy})...")
                self.auditor.remove_duplicates(duplicates, keep_strategy=args.keep_strategy)
                print(f"✓ Removed {self.auditor.audit_results['duplicates_removed']} files")
            else:
                print("No duplicates to remove")

        if args.organize and files:
            if args.organize == "type":
                print("Organizing by file type...")
                self.auditor.organize_by_type(root_id, files)
            elif args.organize == "date":
                print("Organizing by date...")
                self.auditor.organize_by_date(root_id, files)
            print(f"✓ Organized {self.auditor.audit_results['files_organized']} files")

        if args.create_structure:
            print("Creating folder structure...")
            structure = self.load_folder_structure(args.create_structure)
            self.auditor.create_folder_structure(root_id, structure)
            print(f"✓ Created {self.auditor.audit_results['new_folders_created']} folders")

        # Generate report
        self.auditor.generate_audit_report(args.report)

        if args.verbose:
            print("\nAudit Results:")
            print(json.dumps(self.auditor.audit_results, indent=2))


if __name__ == "__main__":
    cli = OneDriveCLI()
    cli.main()
