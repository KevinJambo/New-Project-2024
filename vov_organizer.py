#!/usr/bin/env python3
"""
VOV File Organizer - Simple local file organizer
Scans a folder and organizes files into: Sheet Music, Videos, Pictures, Documents
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class VOVOrganizer:
    """Organize VOV files locally"""

    # File type categories
    CATEGORIES = {
        "Sheet Music": [".pdf", ".musicxml", ".xml", ".mus", ".sib", ".musx"],
        "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".m4v"],
        "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
        "Documents": [".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".odt"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".wma", ".ogg"],
    }

    def __init__(self, source_folder: str, dry_run: bool = True):
        """Initialize organizer"""
        self.source_folder = Path(source_folder)
        self.dry_run = dry_run
        self.results = {
            "total_files": 0,
            "organized_files": 0,
            "skipped_files": 0,
            "new_folders_created": 0,
            "files_by_category": defaultdict(int),
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }

        if not self.source_folder.exists():
            raise ValueError(f"Folder not found: {source_folder}")

    def get_category(self, filename: str) -> str:
        """Determine file category by extension"""
        ext = Path(filename).suffix.lower()

        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category

        return "Other"

    def scan_folder(self) -> dict:
        """Scan folder and categorize files"""
        print(f"\n📂 Scanning: {self.source_folder}\n")

        categorized = defaultdict(list)

        for file_path in self.source_folder.rglob("*"):
            if file_path.is_file():
                # Skip hidden files and system files
                if file_path.name.startswith("."):
                    continue

                self.results["total_files"] += 1
                category = self.get_category(file_path.name)
                categorized[category].append(file_path)
                self.results["files_by_category"][category] += 1

        return categorized

    def print_summary(self, categorized: dict) -> None:
        """Print file summary before organizing"""
        print("=" * 60)
        print("FILE SUMMARY")
        print("=" * 60)

        for category in sorted(categorized.keys()):
            files = categorized[category]
            print(f"\n{category}: {len(files)} files")
            for file_path in sorted(files)[:5]:  # Show first 5
                print(f"  • {file_path.name}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")

        print(f"\nTotal files: {self.results['total_files']}")
        print("=" * 60)

    def create_category_folders(self, categorized: dict) -> None:
        """Create category folders"""
        for category in categorized.keys():
            if category == "Other":
                folder_path = self.source_folder / "Other"
            else:
                folder_path = self.source_folder / category

            if not folder_path.exists():
                if not self.dry_run:
                    folder_path.mkdir(exist_ok=True)
                    print(f"✓ Created folder: {category}/")
                else:
                    print(f"[DRY RUN] Would create: {category}/")
                self.results["new_folders_created"] += 1
            else:
                print(f"→ Folder exists: {category}/")

    def move_files(self, categorized: dict) -> None:
        """Move files to their category folders"""
        print(f"\n{'='*60}")
        print("ORGANIZING FILES")
        print(f"{'='*60}\n")

        for category, files in sorted(categorized.items()):
            if category == "Other":
                target_folder = self.source_folder / "Other"
            else:
                target_folder = self.source_folder / category

            print(f"{category}:")
            for file_path in sorted(files):
                destination = target_folder / file_path.name

                # Skip if file is already in correct folder
                if file_path.parent == target_folder:
                    print(f"  → {file_path.name} (already in place)")
                    self.results["skipped_files"] += 1
                    continue

                # Handle duplicates
                if destination.exists():
                    print(f"  ⚠ {file_path.name} (duplicate exists)")
                    self.results["skipped_files"] += 1
                    continue

                # Move file
                try:
                    if not self.dry_run:
                        shutil.move(str(file_path), str(destination))
                        print(f"  ✓ {file_path.name}")
                    else:
                        print(f"  [DRY RUN] Would move: {file_path.name}")
                    self.results["organized_files"] += 1
                except Exception as e:
                    error_msg = f"Error moving {file_path.name}: {str(e)}"
                    print(f"  ✗ {error_msg}")
                    self.results["errors"].append(error_msg)

    def print_results(self) -> None:
        """Print final results"""
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}")
        print(f"Total files processed: {self.results['total_files']}")
        print(f"Files organized: {self.results['organized_files']}")
        print(f"Files skipped: {self.results['skipped_files']}")
        print(f"New folders created: {self.results['new_folders_created']}")

        if self.results["files_by_category"]:
            print(f"\nFiles by category:")
            for category, count in sorted(self.results["files_by_category"].items()):
                print(f"  • {category}: {count}")

        if self.results["errors"]:
            print(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  ✗ {error}")

        if self.dry_run:
            print(f"\n[DRY RUN MODE] No files were actually moved.")
            print(f"Run with --execute to apply changes.")

        print(f"{'='*60}\n")

    def save_report(self, filename: str = "organization_report.json") -> None:
        """Save organization report"""
        import json
        with open(filename, "w") as f:
            # Convert defaultdict to dict for JSON
            report = {
                "timestamp": self.results["timestamp"],
                "total_files": self.results["total_files"],
                "organized_files": self.results["organized_files"],
                "skipped_files": self.results["skipped_files"],
                "new_folders_created": self.results["new_folders_created"],
                "files_by_category": dict(self.results["files_by_category"]),
                "errors": self.results["errors"]
            }
            json.dump(report, f, indent=2)
        print(f"Report saved to: {filename}")

    def run(self) -> None:
        """Execute organization"""
        try:
            # Scan
            categorized = self.scan_folder()

            if not categorized:
                print("No files found to organize.")
                return

            # Show summary
            self.print_summary(categorized)

            # Ask for confirmation (if not dry run)
            if not self.dry_run:
                response = input("\nProceed with organization? (yes/no): ").strip().lower()
                if response != "yes":
                    print("Cancelled.")
                    return

            # Create folders
            self.create_category_folders(categorized)

            # Move files
            self.move_files(categorized)

            # Print results
            self.print_results()

            # Save report
            self.save_report()

        except Exception as e:
            print(f"Error: {str(e)}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="VOV File Organizer - Organize files by type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vov_organizer.py "/path/to/onedrive/VOV"
  python vov_organizer.py "/path/to/onedrive/VOV" --execute
  python vov_organizer.py "/path/to/onedrive/VOV" --execute --report custom_report.json
        """
    )

    parser.add_argument(
        "folder",
        help="Path to folder to organize"
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually move files (default is dry-run preview)"
    )

    parser.add_argument(
        "--report",
        default="organization_report.json",
        help="Report filename"
    )

    args = parser.parse_args()

    # Create and run organizer
    dry_run = not args.execute
    if dry_run:
        print("\n⚠️  DRY RUN MODE (preview only)")
        print("Use --execute to actually move files\n")

    organizer = VOVOrganizer(args.folder, dry_run=dry_run)
    organizer.run()


if __name__ == "__main__":
    main()
