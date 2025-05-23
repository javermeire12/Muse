#!/usr/bin/env python3
"""
AI File Manager - Simple CLI tool for AI file sharing

This tool manages files shared between multiple AI assistants (Claude, GPT, Gemini, Llama).
It creates and maintains a registry of shared files and provides a way to search, update, and share them.

Usage:
    python aiFileManager.py <command> [options]

Commands:
    register    Register a new file from an AI
    share       Share a file with another AI
    update      Update an existing file
    list        List registered files
    search      Search for files
    describe    Show detailed information about a file

Author:
    Claude (Debugger/Implementer)
"""

import os
import json
import shutil
import argparse
import datetime

# Load configuration from ashConfig_camel.json
CONFIG_PATH = r"C:\Users\jeffv\second_brain\gtp_brain\ashConfig.json"
REGISTRY_PATH = r"C:\Users\jeffv\second_brain\gtp_brain\fileRegistry.json"

# Default configuration (used if config file not found)
DEFAULT_CONFIG = {
    "smartglassImageDir": r"C:\Users\jeffv\Documents\Smartglass_Images",
    "imageMetadataOutput": r"C:\Users\jeffv\second_brain\gtp_brain\data\imageMetadata.json",
    "chatgptMemoryFile": r"C:\Users\jeffv\second_brain\gtp_brain\ChatGPTMemory.json",
    "ashInputFile": r"C:\Users\jeffv\second_brain\gtp_brain\Ash_Input.json",
    "aiCommunicationDir": r"C:\Users\jeffv\second_brain\gtp_brain\aiCommunication",
    "aiSharedDir": r"C:\Users\jeffv\second_brain\gtp_brain\aiShared"
}

# Load configuration
try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # Add aiSharedDir if not in config
        if "aiSharedDir" not in config:
            config["aiSharedDir"] = r"C:\Users\jeffv\second_brain\gtp_brain\aiShared"
    else:
        config = DEFAULT_CONFIG
        # Create config file
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
except Exception as e:
    print(f"Error loading configuration: {str(e)}")
    config = DEFAULT_CONFIG

# Terminal colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def disabled():
        """Disable colors if not supported by terminal"""
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.BOLD = ''
        Colors.END = ''

# Disable colors on Windows if not supported
if os.name == 'nt' and not os.environ.get('ANSICON'):
    Colors.disabled()

# AI roles
AI_ROLES = ["claude", "gpt", "gemini", "llama"]

def loadRegistry():
    """Load the file registry or create it if it doesn't exist."""
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"{Colors.RED}{Colors.BOLD}Error: Registry file is corrupted. Creating new registry.{Colors.END}")
            
            # Backup corrupted registry
            if os.path.exists(REGISTRY_PATH):
                backup_path = f"{REGISTRY_PATH}.bak.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(REGISTRY_PATH, backup_path)
                print(f"{Colors.YELLOW}Backed up corrupted registry to {backup_path}{Colors.END}")
    
    # Return empty registry
    return {}

def saveRegistry(registry):
    """Save the registry to file."""
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)

def updateAshMemory(action, filename, details):
    """
    Update Ash memory with file information.
    
    Args:
        action: Action performed (register, update, share, delete)
        filename: Name of the file
        details: Details of the file
    """
    try:
        ash_path = config["chatgptMemoryFile"]
        if not os.path.exists(ash_path):
            print(f"{Colors.YELLOW}Warning: Ash memory file not found, skipping update{Colors.END}")
            return False
        
        # Load Ash memory
        with open(ash_path, 'r', encoding='utf-8') as f:
            ash_memory = json.load(f)
        
        # Ensure memory array exists
        if "memory" not in ash_memory:
            ash_memory["memory"] = []
        
        # Create insight based on action
        timestamp = datetime.datetime.now().isoformat()
        
        if action == "register":
            insight = f"File '{filename}' registered by {details['creator']} - {details['description']}"
        elif action == "update":
            insight = f"File '{filename}' updated to version {details['version']} - {details['description']}"
        elif action == "share":
            insight = f"File '{filename}' shared with {', '.join(details['sharedWith'])}"
        elif action == "delete":
            insight = f"File '{filename}' deleted from registry"
        else:
            insight = f"File '{filename}' action: {action}"
        
        # Add insight to Ash memory
        ash_memory["memory"].append({
            "timestamp": timestamp,
            "insight": insight
        })
        
        # Save Ash memory
        with open(ash_path, 'w', encoding='utf-8') as f:
            json.dump(ash_memory, f, indent=2)
        
        print(f"{Colors.GREEN}Updated Ash memory with file {action} record{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Failed to update Ash memory: {str(e)}{Colors.END}")
        return False

def registerFile(filename, creator, fileType, description, tags=None, force=False, updateAsh=True):
    """
    Register a file in the system.
    
    Args:
        filename: Path to the file
        creator: ID of the AI that created the file
        fileType: Type of file (code, data, doc, image, other)
        description: Description of the file
        tags: List of tags for the file
        force: Whether to overwrite if file exists
        updateAsh: Whether to update Ash memory
    """
    # Check if file exists
    if not os.path.exists(filename):
        print(f"{Colors.RED}{Colors.BOLD}Error: File '{filename}' does not exist{Colors.END}")
        return False
    
    # Validate creator
    if creator not in AI_ROLES:
        print(f"{Colors.RED}{Colors.BOLD}Error: Unknown AI '{creator}'{Colors.END}")
        print(f"{Colors.YELLOW}Valid options: {', '.join(AI_ROLES)}{Colors.END}")
        return False
    
    # Get base filename
    baseFilename = os.path.basename(filename)
    
    # Load registry
    registry = loadRegistry()
    
    # Check if file already exists in registry
    if baseFilename in registry and not force:
        print(f"{Colors.YELLOW}{Colors.BOLD}File '{baseFilename}' already exists in registry.{Colors.END}")
        print(f"{Colors.YELLOW}Use update command to update it or use --force to overwrite.{Colors.END}")
        return False
    
    # Create destination directory if it doesn't exist
    destDir = os.path.join(config["aiSharedDir"], fileType)
    os.makedirs(destDir, exist_ok=True)
    
    # Copy file to destination
    destPath = os.path.join(destDir, baseFilename)
    shutil.copy2(filename, destPath)
    
    # Create file entry
    fileEntry = {
        "creator": creator,
        "type": fileType,
        "description": description,
        "version": "v1",
        "tags": tags or [],
        "sharedWith": [],
        "status": "active",
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Add to registry
    registry[baseFilename] = fileEntry
    
    # Save registry
    saveRegistry(registry)
    
    # Update Ash memory if requested
    if updateAsh:
        updateAshMemory("register", baseFilename, fileEntry)
    
    print(f"{Colors.GREEN}{Colors.BOLD}File '{baseFilename}' registered successfully{Colors.END}")
    print(f"{Colors.GREEN}Saved to: {destPath}{Colors.END}")
    
    return True

def shareFile(filename, targetAi, updateAsh=True):
    """
    Share a file with another AI.
    
    Args:
        filename: Name of the file
        targetAi: ID of the AI to share with
        updateAsh: Whether to update Ash memory
    """
    # Validate target AI
    if targetAi not in AI_ROLES:
        print(f"{Colors.RED}{Colors.BOLD}Error: Unknown AI '{targetAi}'{Colors.END}")
        print(f"{Colors.YELLOW}Valid options: {', '.join(AI_ROLES)}{Colors.END}")
        return False
    
    # Load registry
    registry = loadRegistry()
    
    # Check if file exists in registry
    if filename not in registry:
        print(f"{Colors.RED}{Colors.BOLD}Error: File '{filename}' not found in registry{Colors.END}")
        return False
    
    # Get file entry
    fileEntry = registry[filename]
    
    # Check if already shared
    if targetAi in fileEntry.get("sharedWith", []):
        print(f"{Colors.YELLOW}File '{filename}' already shared with {targetAi}{Colors.END}")
        return True
    
    # Add target AI to shared_with list
    if "sharedWith" not in fileEntry:
        fileEntry["sharedWith"] = []
    
    fileEntry["sharedWith"].append(targetAi)
    
    # Save registry
    saveRegistry(registry)
    
    # Update Ash memory if requested
    if updateAsh:
        updateAshMemory("share", filename, fileEntry)
    
    # Get file path
    filePath = os.path.join(config["aiSharedDir"], fileEntry["type"], filename)
    
    print(f"{Colors.GREEN}{Colors.BOLD}File '{filename}' shared with {targetAi}{Colors.END}")
    print(f"{Colors.GREEN}Path: {filePath}{Colors.END}")
    
    return True

def updateFile(filename, newVersion=None, description=None, tags=None, updateAsh=True):
    """
    Update a file in the system.
    
    Args:
        filename: Path to the updated file
        newVersion: New version (if None, auto-increment)
        description: New description (if None, keep existing)
        tags: New tags (if None, keep existing)
        updateAsh: Whether to update Ash memory
    """
    # Check if file exists
    if not os.path.exists(filename):
        print(f"{Colors.RED}{Colors.BOLD}Error: File '{filename}' does not exist{Colors.END}")
        return False
    
    # Get base filename
    baseFilename = os.path.basename(filename)
    
    # Load registry
    registry = loadRegistry()
    
    # Check if file exists in registry
    if baseFilename not in registry:
        print(f"{Colors.RED}{Colors.BOLD}Error: File '{baseFilename}' not found in registry{Colors.END}")
        print(f"{Colors.YELLOW}Use register command to register it first.{Colors.END}")
        return False
    
    # Get file entry
    fileEntry = registry[baseFilename]
    
    # Determine new version
    if newVersion is None:
        # Parse current version
        currentVersion = fileEntry["version"]
        if currentVersion.startswith("v"):
            try:
                versionNum = int(currentVersion[1:])
                newVersion = f"v{versionNum + 1}"
            except ValueError:
                newVersion = f"{currentVersion}_updated"
        else:
            newVersion = f"{currentVersion}_updated"
    
    # Update file in destination
    destPath = os.path.join(config["aiSharedDir"], fileEntry["type"], baseFilename)
    
    # Backup existing file if it exists
    if os.path.exists(destPath):
        backupDir = os.path.join(config["aiSharedDir"], "backups")
        os.makedirs(backupDir, exist_ok=True)
        
        backupFilename = f"{os.path.splitext(baseFilename)[0]}_{fileEntry['version']}{os.path.splitext(baseFilename)[1]}"
        backupPath = os.path.join(backupDir, backupFilename)
        
        shutil.copy2(destPath, backupPath)
        print(f"{Colors.BLUE}Backed up previous version to {backupPath}{Colors.END}")
    
    # Copy new file to destination
    shutil.copy2(filename, destPath)
    
    # Update file entry
    fileEntry["version"] = newVersion
    fileEntry["timestamp"] = datetime.datetime.now().isoformat()
    
    # Update description if provided
    if description is not None:
        fileEntry["description"] = description
    
    # Update tags if provided
    if tags is not None:
        fileEntry["tags"] = tags
    
    # Save registry
    saveRegistry(registry)
    
    # Update Ash memory if requested
    if updateAsh:
        updateAshMemory("update", baseFilename, fileEntry)
    
    print(f"{Colors.GREEN}{Colors.BOLD}File '{baseFilename}' updated to {newVersion}{Colors.END}")
    print(f"{Colors.GREEN}Saved to: {destPath}{Colors.END}")
    
    return True

def listFiles(creator=None, fileType=None, tag=None, verbose=False):
    """
    List files in the registry with optional filtering.
    
    Args:
        creator: Filter by creator AI
        fileType: Filter by file type
        tag: Filter by tag
        verbose: Whether to show more details
    """
    # Load registry
    registry = loadRegistry()
    
    # Check if registry is empty
    if not registry:
        print(f"{Colors.YELLOW}No files registered yet.{Colors.END}")
        print(f"{Colors.YELLOW}Use register command to register files.{Colors.END}")
        return []
    
    # Apply filters
    filteredFiles = {}
    
    for filename, entry in registry.items():
        # Filter by creator
        if creator and entry.get("creator") != creator:
            continue
        
        # Filter by file type
        if fileType and entry.get("type") != fileType:
            continue
        
        # Filter by tag
        if tag and tag not in entry.get("tags", []):
            continue
        
        # Add to filtered files
        filteredFiles[filename] = entry
    
    # Check if any files match filters
    if not filteredFiles:
        if creator or fileType or tag:
            print(f"{Colors.YELLOW}No matching files found for the given filters.{Colors.END}")
        else:
            print(f"{Colors.YELLOW}No files registered yet.{Colors.END}")
        return []
    
    # Print files
    print(f"{Colors.GREEN}{Colors.BOLD}Found {len(filteredFiles)} files:{Colors.END}")
    
    for i, (filename, entry) in enumerate(filteredFiles.items(), 1):
        # Format file info
        creator = entry.get("creator", "unknown")
        version = entry.get("version", "v1")
        description = entry.get("description", "")
        tags = entry.get("tags", [])
        sharedWith = entry.get("sharedWith", [])
        fileType = entry.get("type", "unknown")
        timestamp = entry.get("timestamp", "")
        
        # Format timestamp
        if timestamp:
            try:
                dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestampStr = dt.strftime("%Y-%m-%d %H:%M")
            except:
                timestampStr = timestamp
        else:
            timestampStr = "unknown"
        
        # Print file details
        print(f"{i}. {Colors.BOLD}{Colors.BLUE}{filename}{Colors.END} {Colors.YELLOW}({version}){Colors.END}")
        print(f"   Creator: {Colors.CYAN}{creator}{Colors.END} on {timestampStr}")
        print(f"   Type: {fileType}")
        print(f"   Description: {description}")
        
        if sharedWith:
            print(f"   Shared with: {Colors.CYAN}{', '.join(sharedWith)}{Colors.END}")
        
        if tags:
            formattedTags = [f"{Colors.YELLOW}#{tag}{Colors.END}" for tag in tags]
            print(f"   Tags: {' '.join(formattedTags)}")
        
        if verbose:
            filePath = os.path.join(config["aiSharedDir"], fileType, filename)
            print(f"   Path: {filePath}")
            
            if os.path.exists(filePath):
                size = os.path.getsize(filePath)
                print(f"   Size: {formatSize(size)}")
        
        # Add separator between files
        if i < len(filteredFiles):
            print("---")
    
    return list(filteredFiles.keys())

def searchFiles(query, verbose=False):
    """
    Search for files matching a query.
    
    Args:
        query: Search query
        verbose: Whether to show more details
    """
    # Load registry
    registry = loadRegistry()
    
    # Check if registry is empty
    if not registry:
        print(f"{Colors.YELLOW}No files registered yet.{Colors.END}")
        return []
    
    # Search for files
    query = query.lower()
    results = {}
    
    for filename, entry in registry.items():
        # Search in filename
        if query in filename.lower():
            results[filename] = entry
            continue
        
        # Search in description
        if query in entry.get("description", "").lower():
            results[filename] = entry
            continue
        
        # Search in tags
        if any(query in tag.lower() for tag in entry.get("tags", [])):
            results[filename] = entry
            continue
        
        # Search in creator
        if query in entry.get("creator", "").lower():
            results[filename] = entry
            continue
    
    # Check if any files match query
    if not results:
        print(f"{Colors.YELLOW}No files found matching '{query}'.{Colors.END}")
        return []
    
    # Print results
    print(f"{Colors.GREEN}{Colors.BOLD}Found {len(results)} files matching '{query}':{Colors.END}")
    
    for i, (filename, entry) in enumerate(results.items(), 1):
        # Format file info
        creator = entry.get("creator", "unknown")
        version = entry.get("version", "v1")
        description = entry.get("description", "")
        tags = entry.get("tags", [])
        sharedWith = entry.get("sharedWith", [])
        fileType = entry.get("type", "unknown")
        
        # Print file details
        print(f"{i}. {Colors.BOLD}{Colors.BLUE}{filename}{Colors.END} {Colors.YELLOW}({version}){Colors.END}")
        print(f"   Creator: {Colors.CYAN}{creator}{Colors.END}")
        print(f"   Type: {fileType}")
        print(f"   Description: {description}")
        
        if sharedWith:
            print(f"   Shared with: {Colors.CYAN}{', '.join(sharedWith)}{Colors.END}")
        
        if tags:
            formattedTags = [f"{Colors.YELLOW}#{tag}{Colors.END}" for tag in tags]
            print(f"   Tags: {' '.join(formattedTags)}")
        
        if verbose:
            filePath = os.path.join(config["aiSharedDir"], fileType, filename)
            print(f"   Path: {filePath}")
        
        # Add separator between files
        if i < len(results):
            print("---")
    
    return list(results.keys())

def describeFile(filename):
    """
    Show detailed information about a file.
    
    Args:
        filename: Name of the file
    """
    # Load registry
    registry = loadRegistry()
    
    # Check if file exists in registry
    if filename not in registry:
        print(f"{Colors.RED}{Colors.BOLD}Error: File '{filename}' not found in registry{Colors.END}")
        return False
    
    # Get file entry
    entry = registry[filename]
    
    # Get file path
    filePath = os.path.join(config["aiSharedDir"], entry.get("type", "unknown"), filename)
    
    # Print file details
    print(f"{Colors.GREEN}{Colors.BOLD}File Details:{Colors.END}")
    
    # Format file info
    creator = entry.get("creator", "unknown")
    version = entry.get("version", "v1")
    description = entry.get("description", "")
    tags = entry.get("tags", [])
    sharedWith = entry.get("sharedWith", [])
    fileType = entry.get("type", "unknown")
    timestamp = entry.get("timestamp", "")
    
    # Format timestamp
    if timestamp:
        try:
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestampStr = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            timestampStr = timestamp
    else:
        timestampStr = "unknown"
    
    # Print file details
    print(f"{Colors.BOLD}{Colors.BLUE}{filename}{Colors.END} {Colors.YELLOW}({version}){Colors.END}")
    print(f"Creator: {Colors.CYAN}{creator}{Colors.END}")
    print(f"Type: {fileType}")
    print(f"Created: {timestampStr}")
    print(f"Description: {description}")
    
    if sharedWith:
        print(f"Shared with: {Colors.CYAN}{', '.join(sharedWith)}{Colors.END}")
    
    if tags:
        formattedTags = [f"{Colors.YELLOW}#{tag}{Colors.END}" for tag in tags]
        print(f"Tags: {' '.join(formattedTags)}")
    
    print(f"Path: {filePath}")
    
    # Check if file exists
    if not os.path.exists(filePath):
        print(f"{Colors.YELLOW}Warning: File not found at {filePath}{Colors.END}")
        return True
    
    # Print file stats
    stat = os.path.getsize(filePath)
    print(f"Size: {formatSize(stat)}")
    
    # Print modified time
    modifiedTime = datetime.datetime.fromtimestamp(os.path.getmtime(filePath)).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Last modified: {modifiedTime}")
    
    # Print preview for text files
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.txt', '.md', '.py', '.json', '.csv', '.bat', '.sh', '.js', '.html', '.css', '.xml']:
        try:
            with open(filePath, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            if content:
                # Show first 10 lines
                print(f"\n{Colors.BOLD}Preview:{Colors.END}")
                for i, line in enumerate(content[:10]):
                    print(f"{i+1:3d}: {line.rstrip()}")
                
                if len(content) > 10:
                    print("...")
                    print(f"({len(content) - 10} more lines)")
        except Exception as e:
            print(f"{Colors.YELLOW}Could not preview file: {str(e)}{Colors.END}")
    
    return True

def formatSize(sizeBytes):
    """Format file size in human-readable format."""
    if sizeBytes < 1024:
        return f"{sizeBytes} bytes"
    elif sizeBytes < 1024 * 1024:
        return f"{sizeBytes / 1024:.1f} KB"
    elif sizeBytes < 1024 * 1024 * 1024:
        return f"{sizeBytes / (1024 * 1024):.1f} MB"
    else:
        return f"{sizeBytes / (1024 * 1024 * 1024):.1f} GB"

def initDirectories():
    """Initialize the necessary directories."""
    # Create AI shared directory
    os.makedirs(config["aiSharedDir"], exist_ok=True)
    
    # Create subdirectories
    subdirs = ["code", "data", "doc", "image", "other", "backups"]
    for subdir in subdirs:
        os.makedirs(os.path.join(config["aiSharedDir"], subdir), exist_ok=True)
    
    print(f"{Colors.GREEN}{Colors.BOLD}Initialized directory structure at {config['aiSharedDir']}{Colors.END}")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="AI File Manager - Simple CLI tool for AI file sharing"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize the directory structure")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new file from an AI")
    register_parser.add_argument("file", help="Path to the file")
    register_parser.add_argument("creator", help="AI that created the file (claude, gpt, gemini, llama)")
    register_parser.add_argument("type", help="Type of file (code, data, doc, image, other)")
    register_parser.add_argument("description", help="Description of the file")
    register_parser.add_argument("--tags", nargs="+", help="Tags for the file")
    register_parser.add_argument("--force", action="store_true", help="Force overwrite if file exists")
    register_parser.add_argument("--no-ash", action="store_true", help="Don't update Ash memory")
    
    # Share command
    share_parser = subparsers.add_parser("share", help="Share a file with another AI")
    share_parser.add_argument("file", help="Name of the file")
    share_parser.add_argument("ai", help="AI to share with (claude, gpt, gemini, llama)")
    share_parser.add_argument("--no-ash", action="store_true", help="Don't update Ash memory")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update an existing file")
    update_parser.add_argument("file", help="Path to the updated file")
    update