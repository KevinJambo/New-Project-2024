#!/usr/bin/env python3
"""
Example usage of OneDrive Audit Tool
Shows various workflows and use cases
"""

import os
import json
from onedrive_audit import OneDriveAuditor


def example_1_basic_scan():
    """Example 1: Basic folder scan"""
    print("=" * 60)
    print("Example 1: Basic Folder Scan")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()
    files = auditor.scan_folder(root_id)

    print(f"\nFound {len(files)} files")
    print(f"Total size: {auditor.audit_results['total_size'] / (1024**3):.2f} GB")

    # Show first 10 files
    print("\nFirst 10 files:")
    for file_data in files[:10]:
        size_mb = file_data["size"] / (1024**2)
        print(f"  {file_data['path']} ({size_mb:.2f} MB)")


def example_2_find_duplicates():
    """Example 2: Find duplicates"""
    print("\n" + "=" * 60)
    print("Example 2: Find Duplicate Files")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()
    print("\nScanning...")
    files = auditor.scan_folder(root_id)

    print("Finding duplicates...")
    duplicates = auditor.find_duplicates(files)

    if duplicates:
        print(f"\nFound {auditor.audit_results['duplicates_found']} duplicate files:\n")
        for idx, (hash_val, file_list) in enumerate(duplicates.items(), 1):
            print(f"Duplicate set {idx}:")
            for file_data in file_list:
                print(f"  - {file_data['path']} ({file_data['size'] / (1024**2):.2f} MB)")
                print(f"    Modified: {file_data['modified']}")
            print()
    else:
        print("\nNo duplicates found!")


def example_3_remove_duplicates():
    """Example 3: Remove duplicates (keep oldest)"""
    print("\n" + "=" * 60)
    print("Example 3: Remove Duplicates (Keep Oldest)")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()
    print("\nScanning...")
    files = auditor.scan_folder(root_id)

    print("Finding duplicates...")
    duplicates = auditor.find_duplicates(files)

    if duplicates:
        print(f"\nRemoving {auditor.audit_results['duplicates_found']} duplicates...\n")
        auditor.remove_duplicates(duplicates, keep_strategy="oldest")
        print(f"\n✓ Removed {auditor.audit_results['duplicates_removed']} files")
    else:
        print("\nNo duplicates to remove")


def example_4_organize_by_type():
    """Example 4: Organize files by type"""
    print("\n" + "=" * 60)
    print("Example 4: Organize Files by Type")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()
    print("\nScanning...")
    files = auditor.scan_folder(root_id)

    print("Creating file type structure...")
    auditor.organize_by_type(root_id, files)

    print(f"\n✓ Created {auditor.audit_results['new_folders_created']} type folders")
    print(f"✓ Organized {auditor.audit_results['files_organized']} files")


def example_5_organize_by_date():
    """Example 5: Organize files by date"""
    print("\n" + "=" * 60)
    print("Example 5: Organize Files by Date (Year/Month)")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()
    print("\nScanning...")
    files = auditor.scan_folder(root_id)

    print("Creating date structure...")
    auditor.organize_by_date(root_id, files)

    print(f"\n✓ Created date folders")
    print(f"✓ Organized {auditor.audit_results['files_organized']} files")


def example_6_create_custom_structure():
    """Example 6: Create custom folder structure"""
    print("\n" + "=" * 60)
    print("Example 6: Create Custom Folder Structure")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()

    # Define custom structure
    structure = {
        "Personal": {
            "Documents": {},
            "Photos": {},
            "Videos": {}
        },
        "Work": {
            "Projects": {},
            "Reports": {},
            "Meetings": {}
        },
        "Archive": {}
    }

    print("\nCreating custom structure:")
    auditor.create_folder_structure(root_id, structure)

    print(f"\n✓ Created {auditor.audit_results['new_folders_created']} folders")


def example_7_full_audit():
    """Example 7: Complete audit workflow"""
    print("\n" + "=" * 60)
    print("Example 7: Complete Audit Workflow")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()

    # Step 1: Scan
    print("\n[1] Scanning OneDrive...")
    files = auditor.scan_folder(root_id)
    print(f"✓ Found {len(files)} files ({auditor.audit_results['total_size'] / (1024**3):.2f} GB)")

    # Step 2: Find duplicates
    print("\n[2] Finding duplicates...")
    duplicates = auditor.find_duplicates(files)
    if duplicates:
        print(f"✓ Found {auditor.audit_results['duplicates_found']} duplicates")

        # Step 3: Remove duplicates
        print("\n[3] Removing duplicates...")
        auditor.remove_duplicates(duplicates, keep_strategy="oldest")
        print(f"✓ Removed {auditor.audit_results['duplicates_removed']} files")

    # Step 4: Organize
    print("\n[4] Organizing files...")
    auditor.organize_by_type(root_id, files)
    print(f"✓ Organized {auditor.audit_results['files_organized']} files")

    # Step 5: Generate report
    print("\n[5] Generating report...")
    auditor.generate_audit_report("full_audit_report.json")
    print("✓ Report saved to full_audit_report.json")


def example_8_detailed_report():
    """Example 8: Generate detailed report"""
    print("\n" + "=" * 60)
    print("Example 8: Generate Detailed Report")
    print("=" * 60)

    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    auditor = OneDriveAuditor(client_id)

    if not auditor.authenticate():
        return

    root_id = auditor.get_drive_root()
    print("\nScanning...")
    files = auditor.scan_folder(root_id)

    # Analyze file types
    file_types = {}
    for file_data in files:
        ext = file_data["name"].split(".")[-1].lower() if "." in file_data["name"] else "no_extension"
        if ext not in file_types:
            file_types[ext] = {"count": 0, "size": 0}
        file_types[ext]["count"] += 1
        file_types[ext]["size"] += file_data["size"]

    print("\nFile Type Analysis:")
    print(f"{'Extension':<15} {'Count':<10} {'Size (MB)':<15}")
    print("-" * 40)
    for ext, data in sorted(file_types.items(), key=lambda x: x[1]["size"], reverse=True)[:10]:
        size_mb = data["size"] / (1024**2)
        print(f"{ext:<15} {data['count']:<10} {size_mb:<15.2f}")

    # Find largest files
    print("\nLargest Files:")
    largest = sorted(files, key=lambda x: x["size"], reverse=True)[:10]
    for idx, file_data in enumerate(largest, 1):
        size_mb = file_data["size"] / (1024**2)
        print(f"{idx}. {file_data['path']} - {size_mb:.2f} MB")

    # Generate comprehensive report
    report_data = {
        "summary": auditor.audit_results,
        "file_types": file_types,
        "total_files": len(files),
        "file_type_count": len(file_types)
    }

    with open("detailed_report.json", "w") as f:
        json.dump(report_data, f, indent=2)

    print("\n✓ Detailed report saved to detailed_report.json")


def main():
    """Run examples"""
    if not os.getenv("ONEDRIVE_CLIENT_ID"):
        print("Error: ONEDRIVE_CLIENT_ID environment variable not set")
        print("Please set it before running examples")
        return

    print("\nOneDrive Audit Tool - Examples")
    print("\nChoose an example to run:")
    print("1. Basic folder scan")
    print("2. Find duplicate files")
    print("3. Remove duplicates")
    print("4. Organize files by type")
    print("5. Organize files by date")
    print("6. Create custom folder structure")
    print("7. Complete audit workflow")
    print("8. Generate detailed report")

    choice = input("\nEnter choice (1-8): ").strip()

    examples = {
        "1": example_1_basic_scan,
        "2": example_2_find_duplicates,
        "3": example_3_remove_duplicates,
        "4": example_4_organize_by_type,
        "5": example_5_organize_by_date,
        "6": example_6_create_custom_structure,
        "7": example_7_full_audit,
        "8": example_8_detailed_report,
    }

    if choice in examples:
        examples[choice]()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
