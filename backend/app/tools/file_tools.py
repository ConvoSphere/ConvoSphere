"""
File tools for reading and writing files.

This module provides tools for file operations including reading,
writing, and basic file management.
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from loguru import logger


def read_file(file_path: str, user_id: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file
        user_id: User ID for tracking
        encoding: File encoding
        
    Returns:
        Dict[str, Any]: File content and metadata
    """
    try:
        # Validate file path
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Check file size (limit to 10MB)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return {
                "success": False,
                "error": f"File too large: {file_size} bytes (max 10MB)"
            }
        
        # Determine file type
        file_ext = Path(file_path).suffix.lower()
        
        # Read file based on type
        if file_ext in ['.json']:
            with open(file_path, 'r', encoding=encoding) as f:
                content = json.load(f)
                content_type = "json"
        elif file_ext in ['.csv']:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                content = list(reader)
                content_type = "csv"
        elif file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                content_type = "text"
        else:
            # Try to read as text
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    content_type = "text"
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "error": f"Cannot read file as text: {file_path}"
                }
        
        return {
            "success": True,
            "content": content,
            "content_type": content_type,
            "file_path": file_path,
            "file_size": file_size,
            "file_extension": file_ext
        }
        
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def write_file(file_path: str, content: Union[str, Dict, List], user_id: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        user_id: User ID for tracking
        encoding: File encoding
        
    Returns:
        Dict[str, Any]: Write operation result
    """
    try:
        # Validate file path
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
        
        # Determine file type and write accordingly
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.json']:
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        elif file_ext in ['.csv'] and isinstance(content, list):
            if content and isinstance(content[0], dict):
                fieldnames = content[0].keys()
                with open(file_path, 'w', encoding=encoding, newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(content)
            else:
                return {
                    "success": False,
                    "error": "CSV content must be a list of dictionaries"
                }
        else:
            # Write as text
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(str(content))
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_size": file_size,
            "content_length": len(str(content))
        }
        
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_files(directory: str, user_id: str, pattern: str = "*") -> Dict[str, Any]:
    """
    List files in a directory.
    
    Args:
        directory: Directory path
        user_id: User ID for tracking
        pattern: File pattern to match
        
    Returns:
        Dict[str, Any]: List of files and metadata
    """
    try:
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"Path is not a directory: {directory}"
            }
        
        # List files
        files = []
        for file_path in Path(directory).glob(pattern):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "extension": file_path.suffix.lower()
                })
        
        return {
            "success": True,
            "directory": directory,
            "pattern": pattern,
            "files": files,
            "count": len(files)
        }
        
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_file_info(file_path: str, user_id: str) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        user_id: User ID for tracking
        
    Returns:
        Dict[str, Any]: File information
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        stat = os.stat(file_path)
        path_obj = Path(file_path)
        
        return {
            "success": True,
            "name": path_obj.name,
            "path": str(path_obj),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": path_obj.suffix.lower(),
            "is_file": path_obj.is_file(),
            "is_directory": path_obj.is_dir(),
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK)
        }
        
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_file(file_path: str, user_id: str) -> Dict[str, Any]:
    """
    Delete a file.
    
    Args:
        file_path: Path to the file
        user_id: User ID for tracking
        
    Returns:
        Dict[str, Any]: Delete operation result
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}"
            }
        
        # Get file info before deletion
        file_info = get_file_info(file_path, user_id)
        
        # Delete file
        os.remove(file_path)
        
        return {
            "success": True,
            "deleted_file": file_info.get("success") and file_info or None,
            "message": f"File deleted: {file_path}"
        }
        
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def create_directory(directory: str, user_id: str) -> Dict[str, Any]:
    """
    Create a directory.
    
    Args:
        directory: Directory path
        user_id: User ID for tracking
        
    Returns:
        Dict[str, Any]: Create operation result
    """
    try:
        if os.path.exists(directory):
            return {
                "success": False,
                "error": f"Directory already exists: {directory}"
            }
        
        # Create directory
        os.makedirs(directory, exist_ok=True)
        
        return {
            "success": True,
            "directory": directory,
            "message": f"Directory created: {directory}"
        }
        
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def copy_file(source_path: str, destination_path: str, user_id: str) -> Dict[str, Any]:
    """
    Copy a file.
    
    Args:
        source_path: Source file path
        destination_path: Destination file path
        user_id: User ID for tracking
        
    Returns:
        Dict[str, Any]: Copy operation result
    """
    try:
        if not os.path.exists(source_path):
            return {
                "success": False,
                "error": f"Source file not found: {source_path}"
            }
        
        if not os.path.isfile(source_path):
            return {
                "success": False,
                "error": f"Source path is not a file: {source_path}"
            }
        
        # Create destination directory if needed
        dest_dir = os.path.dirname(destination_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(source_path, destination_path)
        
        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "message": f"File copied: {source_path} -> {destination_path}"
        }
        
    except Exception as e:
        logger.error(f"Error copying file {source_path} to {destination_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        } 