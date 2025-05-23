#!/usr/bin/env python3
"""
Second Brain camelCase Converter

This script is specifically designed to convert the file structure of the 
C:\Users\jeffv\second_brain directory to use consistent camelCase naming.

It handles:
- Snake_case to camelCase conversion (folder_name → folderName)
- Hyphenated names to camelCase (file-name → fileName)
- Special handling for date prefixes
- Creates backups before making any changes

Usage:
    python second_brain_converter.py [--dry-run] [--no-backup]

Options:
    --dry-run     Show what would be renamed without making changes
    --no-backup   Skip creating backups (not recommended)
"""

import os
import sys
import re
import shutil
import argparse
import datetime
from pathlib import Path

# Configuration
ROOT_DIR = r"C:\Users\jeffv\second_brain"
BACKUP_DIR = os.path.join(ROOT_DIR, "conversion_backup")

# Files/folders to exclude from renaming
EXCLUSIONS = [
    ".env",           # Environment file should stay as-is
    "ChatGPTMemory.json",  # Keep this filename as is for compatibility
    "processed_inputs",  # Keep this as-is for Ash compatibility
]

# Special patterns
DATE_PREFIX_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})[-_](.+)$")

def to_camel_case(text, preserve_date_prefix=True):
    """
    Convert text to camelCase, with special handling for date prefixes.
    
    Args:
        text: Text to convert
        preserve_date_prefix: Whether to preserve date prefixes (YYYY-MM-DD_)
    
    Returns:
        camelCase version of text
    """
    # Handle date prefixes if needed
    if preserve_date_prefix:
        date_match = DATE_PREFIX_PATTERN.match(text)
        if date_match:
            date_part = date_match.group(1)
            rest = date_match.group(2)
            # Convert the part after the date to camelCase
            camel_rest = to_camel_case(rest, preserve_date_prefix=False)
            return f"{date_part}_{camel_rest}"
    
    # Handle file extensions
    base_name, ext = os.path.splitext(text)
    
    # Split by separators
    parts = re.split(r'[_\-\s]+', base_name)
    
    # If only one part and no separators, leave it as is
    if len(parts) == 1 and parts[0] == base_name:
        return text
    
    # Convert to camelCase: first word lowercase, others capitalized
    camel = parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
    
    # Add extension back
    return camel + ext

def should_exclude(path):
    """Check if a path should be excluded from renaming."""
    name = os.path.basename(path)
    
    # Check direct exclusions
    if name in EXCLUSIONS:
        return True
    
    # Add any other exclusion logic here
    
    return False

def create_backup():
    """Create a backup of the entire directory structure."""
    print(f"Creating backup of {ROOT_DIR} to {BACKUP_DIR}...")
    
    # Create a unique backup directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}_{timestamp}"
    
    try:
        # Copy all files and directories
        shutil.copytree(ROOT_DIR, backup_path, ignore=shutil.ignore_patterns('conversion_backup*'))
        print(f"✅ Backup created successfully at {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {str(e)}")
        return None

def rename_to_camel_case(dry_run=False):
    """
    Rename all files and directories to camelCase.
    
    Args:
        dry_run: If True, only show what would be renamed without making changes
    """
    # Get all paths (deepest first to avoid path changes affecting child renames)
    all_paths = []
    for root, dirs, files in os.walk(ROOT_DIR, topdown=False):
        # Add directories
        for d in dirs:
            path = os.path.join(root, d)
            all_paths.append(path)
        
        # Add files
        for f in files:
            path = os.path.join(root, f)
            all_paths.append(path)
    
    # Process each path
    renamed = 0
    for path in all_paths:
        # Skip if in exclusion list
        if should_exclude(path):
            if dry_run:
                print(f"⚠️ Skipping (excluded): {path}")
            continue
        
        # Get parent directory and name
        parent = os.path.dirname(path)
        name = os.path.basename(path)
        
        # Convert to camelCase
        camel_name = to_camel_case(name)
        
        # Skip if already in camelCase or no change
        if camel_name == name:
            continue
        
        # New path
        new_path = os.path.join(parent, camel_name)
        
        # Check if destination exists
        if os.path.exists(new_path):
            print(f"⚠️ Cannot rename: {path} → {new_path} (destination exists)")
            continue
        
        # Rename
        if dry_run:
            print(f"Would rename: {path} → {new_path}")
        else:
            try:
                os.rename(path, new_path)
                print(f"✅ Renamed: {path} → {new_path}")
                renamed += 1
            except Exception as e:
                print(f"❌ Error renaming {path}: {str(e)}")
    
    return renamed

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert Second Brain structure to camelCase")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be renamed without making changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backups (not recommended)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Second Brain camelCase Converter")
    print("=" * 60)
    print(f"Target directory: {ROOT_DIR}")
    print(f"Mode: {'Dry run (no changes)' if args.dry_run else 'Live conversion'}")
    print("-" * 60)
    
    # Create backup unless skipped
    if not args.no_backup and not args.dry_run:
        backup_path = create_backup()
        if not backup_path:
            retry = input("Backup failed. Continue without backup? (y/n): ")
            if retry.lower() != 'y':
                print("Operation cancelled.")
                return
    
    # Perform renaming
    renamed = rename_to_camel_case(dry_run=args.dry_run)
    
    print("-" * 60)
    if args.dry_run:
        print(f"Dry run complete. {renamed} items would be renamed.")
    else:
        print(f"Conversion complete. {renamed} items renamed to camelCase.")
    
    print("\nRecommended next steps:")
    print("1. Review the changes to ensure everything converted correctly")
    print("2. Update any scripts or tools that might reference the renamed paths")
    print("=" * 60)

if __name__ == "__main__":
    main()
