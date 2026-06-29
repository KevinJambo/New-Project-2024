#!/usr/bin/env python3
"""
ZIP Cleaner - Extract and organize files from ZIP archives
Works with vov_organizer.py to organize extracted contents
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class ZIPCleaner:
    """Extract and organize ZIP files"""

    def __init__(self, source_folder: str, extract_here: bool = True, dry_run: bool = True):
        """
        Initialize ZIP cleaner

        Args:
            source_folder: Folder containing ZIP files
            extract_here: Extract in same folder (True) or subfolder (False)
            dry_run: Preview mode (True) or actually extract (False)
        """
        self.source_folder = Path(source_folder)
        self.extract_here = extract_here
        self.dry_run = dry_run
        self.results = {
            "total_zips": 0,
            "successfully_extracted": 0,
            "failed_extractions": 0,
            "total_files_extracted": 0,
            "total_size_freed": 0,
            "zips_deleted": 0,
            "extraction_details": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }

        if not self.source_folder.exists():
            raise ValueError(f"Folder not found: {source_folder}")

    def find_zip_files(self) -> list:
        """Find all ZIP files in folder"""
        print(f"\n🔍 Scanning for ZIP files: {self.source_folder}\n")

        zip_files = []
        for file_path in self.source_folder.rglob("*.zip"):
            if file_path.is_file():
                zip_files.append(file_path)
                size_mb = file_path.stat().st_size / (1024 ** 2)
                print(f"  Found: {file_path.name} ({size_mb:.2f} MB)")

        self.results["total_zips"] = len(zip_files)
        return sorted(zip_files)

    def print_zip_contents(self, zip_path: Path) -> dict:
        """Show what's in a ZIP file"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                files = zf.namelist()
                total_size = sum(zf.getinfo(name).file_size for name in files)

                return {
                    "files": files,
                    "count": len(files),
                    "total_size": total_size
                }
        except Exception as e:
            print(f"  Error reading ZIP: {str(e)}")
            return {"files": [], "count": 0, "total_size": 0}

    def extract_zip(self, zip_path: Path) -> bool:
        """Extract a single ZIP file"""
        try:
            if self.extract_here:
                extract_to = zip_path.parent
            else:
                # Create subfolder named after ZIP
                extract_to = zip_path.parent / zip_path.stem
                if not extract_to.exists() and not self.dry_run:
                    extract_to.mkdir(exist_ok=True)

            if not self.dry_run:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(extract_to)

            return True
        except Exception as e:
            print(f"  Error extracting: {str(e)}")
            self.results["errors"].append(f"{zip_path.name}: {str(e)}")
            return False

    def delete_zip(self, zip_path: Path) -> bool:
        """Delete ZIP file after extraction"""
        try:
            if not self.dry_run:
                zip_size = zip_path.stat().st_size
                zip_path.unlink()
                self.results["total_size_freed"] += zip_size
                self.results["zips_deleted"] += 1
            return True
        except Exception as e:
            print(f"  Error deleting ZIP: {str(e)}")
            self.results["errors"].append(f"Delete failed: {str(e)}")
            return False

    def process_zips(self, delete_after: bool = False) -> None:
        """Process all ZIP files"""
        zip_files = self.find_zip_files()

        if not zip_files:
            print("No ZIP files found.")
            return

        print(f"\n{'='*60}")
        print("ZIP EXTRACTION PLAN")
        print(f"{'='*60}\n")

        for zip_path in zip_files:
            print(f"📦 {zip_path.name}")

            # Show contents
            contents = self.print_zip_contents(zip_path)
            print(f"   Files: {contents['count']}")
            print(f"   Size: {contents['total_size'] / (1024**2):.2f} MB")

            if contents["files"]:
                print(f"   Sample files:")
                for file_name in contents["files"][:3]:
                    print(f"     • {file_name}")
                if len(contents["files"]) > 3:
                    print(f"     ... and {len(contents['files']) - 3} more")

            if self.extract_here:
                print(f"   Extract to: {zip_path.parent}/")
            else:
                print(f"   Extract to: {zip_path.parent / zip_path.stem}/")

            if delete_after:
                print(f"   Action: DELETE after extraction")
            print()

        # Confirmation
        print(f"{'='*60}")
        if self.dry_run:
            print("[DRY RUN MODE] No changes will be made")
            response = input("Continue with analysis? (yes/no): ").strip().lower()
        else:
            response = input("Proceed with extraction? (yes/no): ").strip().lower()

        if response != "yes":
            print("Cancelled.")
            return

        # Process
        print(f"\n{'='*60}")
        print("EXTRACTING FILES")
        print(f"{'='*60}\n")

        for zip_path in zip_files:
            print(f"📦 {zip_path.name}")

            # Extract
            if self.dry_run:
                print(f"  [DRY RUN] Would extract to {zip_path.parent}")
                self.results["successfully_extracted"] += 1
                self.results["total_files_extracted"] += self.print_zip_contents(zip_path)["count"]
            else:
                if self.extract_zip(zip_path):
                    print(f"  ✓ Extracted")
                    self.results["successfully_extracted"] += 1
                    self.results["total_files_extracted"] += self.print_zip_contents(zip_path)["count"]

                    # Delete if requested
                    if delete_after:
                        if self.delete_zip(zip_path):
                            print(f"  ✓ Deleted ZIP")
                        else:
                            print(f"  ✗ Failed to delete ZIP")
                            self.results["failed_extractions"] += 1
                else:
                    print(f"  ✗ Extraction failed")
                    self.results["failed_extractions"] += 1

        # Results
        self.print_results()

    def print_results(self) -> None:
        """Print results"""
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}")
        print(f"Total ZIP files: {self.results['total_zips']}")
        print(f"Successfully extracted: {self.results['successfully_extracted']}")
        print(f"Failed extractions: {self.results['failed_extractions']}")
        print(f"Total files extracted: {self.results['total_files_extracted']}")

        if self.results['total_size_freed'] > 0:
            freed_mb = self.results['total_size_freed'] / (1024 ** 2)
            print(f"Space freed: {freed_mb:.2f} MB")

        if self.results['zips_deleted'] > 0:
            print(f"ZIP files deleted: {self.results['zips_deleted']}")

        if self.results["errors"]:
            print(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  ✗ {error}")

        if self.dry_run:
            print(f"\n[DRY RUN MODE] No files were actually extracted or deleted.")

        print(f"{'='*60}\n")

    def save_report(self, filename: str = "zip_extraction_report.json") -> None:
        """Save extraction report"""
        import json
        with open(filename, "w") as f:
            report = {
                "timestamp": self.results["timestamp"],
                "total_zips": self.results["total_zips"],
                "successfully_extracted": self.results["successfully_extracted"],
                "failed_extractions": self.results["failed_extractions"],
                "total_files_extracted": self.results["total_files_extracted"],
                "space_freed_bytes": self.results["total_size_freed"],
                "zips_deleted": self.results["zips_deleted"],
                "errors": self.results["errors"]
            }
            json.dump(report, f, indent=2)
        print(f"Report saved to: {filename}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ZIP Cleaner - Extract and organize ZIP files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python zip_cleaner.py "C:\\path\\to\\folder"
  python zip_cleaner.py "C:\\path\\to\\folder" --extract --delete
  python zip_cleaner.py "C:\\path\\to\\folder" --extract --delete --subfolder
        """
    )

    parser.add_argument(
        "folder",
        help="Path to folder containing ZIP files"
    )

    parser.add_argument(
        "--extract",
        action="store_true",
        help="Actually extract files (default is dry-run preview)"
    )

    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete ZIP files after extraction"
    )

    parser.add_argument(
        "--subfolder",
        action="store_true",
        help="Extract into subfolders (default: extract in same folder)"
    )

    parser.add_argument(
        "--report",
        default="zip_extraction_report.json",
        help="Report filename"
    )

    args = parser.parse_args()

    # Create and run cleaner
    dry_run = not args.extract
    if dry_run:
        print("\n⚠️  DRY RUN MODE (preview only)")
        print("Use --extract to actually extract files\n")

    cleaner = ZIPCleaner(
        args.folder,
        extract_here=not args.subfolder,
        dry_run=dry_run
    )
    cleaner.process_zips(delete_after=args.delete)
    cleaner.save_report(args.report)


if __name__ == "__main__":
    main()
