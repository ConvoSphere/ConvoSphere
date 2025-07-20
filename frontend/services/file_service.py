"""
File service for handling file uploads and downloads.

This module provides comprehensive file management functionality including
upload, download, progress tracking, and file validation.
"""

import asyncio
import json
import aiohttp
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from .http_client import http_client
from .error_handler import handle_api_error, handle_network_error
from utils.helpers import generate_id, format_file_size
from utils.validators import validate_file_data


class FileStatus(Enum):
    """File upload status enumeration."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileType(Enum):
    """File type enumeration."""
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    OTHER = "other"


@dataclass
class FileMetadata:
    """File metadata information."""
    filename: str
    file_size: int
    mime_type: str
    file_type: FileType
    checksum: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None


@dataclass
class UploadProgress:
    """Upload progress information."""
    file_id: str
    filename: str
    bytes_uploaded: int
    total_bytes: int
    percentage: float
    status: FileStatus
    start_time: datetime
    estimated_time_remaining: Optional[float] = None
    upload_speed: Optional[float] = None


class FileService:
    """Service for file upload and download management."""
    
    def __init__(self):
        """Initialize the file service."""
        self.uploads: Dict[str, UploadProgress] = {}
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.supported_types = {
            # Documents
            "application/pdf": FileType.DOCUMENT,
            "application/msword": FileType.DOCUMENT,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCUMENT,
            "text/plain": FileType.DOCUMENT,
            "text/markdown": FileType.DOCUMENT,
            "text/html": FileType.DOCUMENT,
            "application/json": FileType.DOCUMENT,
            "text/csv": FileType.DOCUMENT,
            
            # Images
            "image/jpeg": FileType.IMAGE,
            "image/png": FileType.IMAGE,
            "image/gif": FileType.IMAGE,
            "image/webp": FileType.IMAGE,
            "image/svg+xml": FileType.IMAGE,
            
            # Audio
            "audio/mpeg": FileType.AUDIO,
            "audio/wav": FileType.AUDIO,
            "audio/ogg": FileType.AUDIO,
            "audio/mp4": FileType.AUDIO,
            
            # Video
            "video/mp4": FileType.VIDEO,
            "video/webm": FileType.VIDEO,
            "video/ogg": FileType.VIDEO,
            
            # Archives
            "application/zip": FileType.ARCHIVE,
            "application/x-rar-compressed": FileType.ARCHIVE,
            "application/x-7z-compressed": FileType.ARCHIVE,
            "application/gzip": FileType.ARCHIVE,
        }
    
    def validate_file(self, file_data: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """
        Validate file before upload.
        
        Args:
            file_data: File content as bytes
            filename: Name of the file
            mime_type: MIME type of the file
            
        Returns:
            Validation result with success status and errors
        """
        errors = []
        
        # Check file size
        if len(file_data) > self.max_file_size:
            errors.append(f"File size exceeds maximum limit of {format_file_size(self.max_file_size)}")
        
        # Check file type
        if mime_type not in self.supported_types:
            errors.append(f"Unsupported file type: {mime_type}")
        
        # Check filename
        if not filename or len(filename) > 255:
            errors.append("Invalid filename")
        
        # Check for dangerous file extensions
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js']
        file_extension = Path(filename).suffix.lower()
        if file_extension in dangerous_extensions:
            errors.append(f"Dangerous file extension: {file_extension}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "file_type": self.supported_types.get(mime_type, FileType.OTHER)
        }
    
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        mime_type: str,
        endpoint: str = "/api/v1/files/upload",
        metadata: Optional[Dict[str, Any]] = None,
        on_progress: Optional[Callable[[UploadProgress], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """
        Upload a file with progress tracking.
        
        Args:
            file_data: File content as bytes
            filename: Name of the file
            mime_type: MIME type of the file
            endpoint: Upload endpoint
            metadata: Additional metadata
            on_progress: Progress callback function
            on_complete: Completion callback function
            on_error: Error callback function
            
        Returns:
            File ID if successful, None otherwise
        """
        # Validate file
        validation = self.validate_file(file_data, filename, mime_type)
        if not validation["valid"]:
            error_msg = "; ".join(validation["errors"])
            if on_error:
                on_error(error_msg)
            return None
        
        # Generate file ID
        file_id = generate_id()
        
        # Create upload progress
        progress = UploadProgress(
            file_id=file_id,
            filename=filename,
            bytes_uploaded=0,
            total_bytes=len(file_data),
            percentage=0.0,
            status=FileStatus.UPLOADING,
            start_time=datetime.now()
        )
        
        self.uploads[file_id] = progress
        
        try:
            # Prepare upload data
            upload_data = {
                "filename": filename,
                "mime_type": mime_type,
                "file_size": len(file_data),
                "file_type": validation["file_type"].value,
                "metadata": metadata or {}
            }
            
            # Create multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field('file', file_data, filename=filename, content_type=mime_type)
            form_data.add_field('metadata', json.dumps(upload_data))
            
            # Upload file with progress tracking
            async with http_client.session.post(
                f"{http_client.base_url}{endpoint}",
                data=form_data,
                headers={"Authorization": http_client.headers.get("Authorization", "")}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    progress.status = FileStatus.COMPLETED
                    progress.percentage = 100.0
                    progress.bytes_uploaded = progress.total_bytes
                    
                    if on_progress:
                        on_progress(progress)
                    
                    if on_complete:
                        on_complete(result)
                    
                    return result.get("file_id")
                else:
                    error_text = await response.text()
                    raise Exception(f"Upload failed: {response.status} - {error_text}")
                    
        except Exception as e:
            progress.status = FileStatus.FAILED
            error_msg = str(e)
            
            if on_progress:
                on_progress(progress)
            
            if on_error:
                on_error(error_msg)
            
            return None
    
    async def upload_file_chunked(
        self,
        file_path: str,
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        endpoint: str = "/api/v1/files/upload-chunked",
        metadata: Optional[Dict[str, Any]] = None,
        on_progress: Optional[Callable[[UploadProgress], None]] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """
        Upload a large file in chunks.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of each chunk in bytes
            endpoint: Upload endpoint
            metadata: Additional metadata
            on_progress: Progress callback function
            on_complete: Completion callback function
            on_error: Error callback function
            
        Returns:
            File ID if successful, None otherwise
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                if on_error:
                    on_error("File not found")
                return None
            
            filename = file_path_obj.name
            file_size = file_path_obj.stat().st_size
            
            # Determine MIME type
            mime_type = self._get_mime_type(filename)
            
            # Validate file
            with open(file_path, 'rb') as f:
                sample_data = f.read(min(1024, file_size))  # Read first 1KB for validation
            
            validation = self.validate_file(sample_data, filename, mime_type)
            if not validation["valid"]:
                error_msg = "; ".join(validation["errors"])
                if on_error:
                    on_error(error_msg)
                return None
            
            # Generate file ID
            file_id = generate_id()
            
            # Create upload progress
            progress = UploadProgress(
                file_id=file_id,
                filename=filename,
                bytes_uploaded=0,
                total_bytes=file_size,
                percentage=0.0,
                status=FileStatus.UPLOADING,
                start_time=datetime.now()
            )
            
            self.uploads[file_id] = progress
            
            # Initialize chunked upload
            init_data = {
                "file_id": file_id,
                "filename": filename,
                "mime_type": mime_type,
                "file_size": file_size,
                "chunk_size": chunk_size,
                "metadata": metadata or {}
            }
            
            async with http_client.session.post(
                f"{http_client.base_url}{endpoint}/init",
                json=init_data,
                headers={"Authorization": http_client.headers.get("Authorization", "")}
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to initialize chunked upload")
                
                init_result = await response.json()
                upload_id = init_result["upload_id"]
            
            # Upload chunks
            chunk_index = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk_data = f.read(chunk_size)
                    if not chunk_data:
                        break
                    
                    # Upload chunk
                    chunk_form = aiohttp.FormData()
                    chunk_form.add_field('chunk', chunk_data)
                    chunk_form.add_field('upload_id', upload_id)
                    chunk_form.add_field('chunk_index', str(chunk_index))
                    
                    async with http_client.session.post(
                        f"{http_client.base_url}{endpoint}/chunk",
                        data=chunk_form,
                        headers={"Authorization": http_client.headers.get("Authorization", "")}
                    ) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to upload chunk {chunk_index}")
                    
                    # Update progress
                    progress.bytes_uploaded += len(chunk_data)
                    progress.percentage = (progress.bytes_uploaded / progress.total_bytes) * 100
                    
                    if on_progress:
                        on_progress(progress)
                    
                    chunk_index += 1
            
            # Finalize upload
            finalize_data = {"upload_id": upload_id}
            async with http_client.session.post(
                f"{http_client.base_url}{endpoint}/finalize",
                json=finalize_data,
                headers={"Authorization": http_client.headers.get("Authorization", "")}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    progress.status = FileStatus.COMPLETED
                    progress.percentage = 100.0
                    
                    if on_progress:
                        on_progress(progress)
                    
                    if on_complete:
                        on_complete(result)
                    
                    return result.get("file_id")
                else:
                    raise Exception("Failed to finalize upload")
                    
        except Exception as e:
            if file_id in self.uploads:
                self.uploads[file_id].status = FileStatus.FAILED
            
            error_msg = str(e)
            if on_error:
                on_error(error_msg)
            
            return None
    
    async def download_file(
        self,
        file_id: str,
        destination_path: Optional[str] = None,
        on_progress: Optional[Callable[[float], None]] = None
    ) -> Optional[str]:
        """
        Download a file.
        
        Args:
            file_id: ID of the file to download
            destination_path: Path to save the file (optional)
            on_progress: Progress callback function
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Get file info first
            file_info = await self.get_file_info(file_id)
            if not file_info:
                return None
            
            if not destination_path:
                destination_path = f"/tmp/{file_info['filename']}"
            
            # Download file
            async with http_client.session.get(
                f"{http_client.base_url}/api/v1/files/{file_id}/download",
                headers={"Authorization": http_client.headers.get("Authorization", "")}
            ) as response:
                if response.status == 200:
                    with open(destination_path, 'wb') as f:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded = 0
                        
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if on_progress and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                on_progress(progress)
                    
                    return destination_path
                else:
                    raise Exception(f"Download failed: {response.status}")
                    
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    async def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information."""
        try:
            response = await http_client.get(f"/api/v1/files/{file_id}")
            return response if response else None
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        try:
            response = await http_client.delete(f"/api/v1/files/{file_id}")
            return response is not None
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_upload_progress(self, file_id: str) -> Optional[UploadProgress]:
        """Get upload progress for a file."""
        return self.uploads.get(file_id)
    
    def cancel_upload(self, file_id: str) -> bool:
        """Cancel an upload."""
        if file_id in self.uploads:
            self.uploads[file_id].status = FileStatus.CANCELLED
            return True
        return False
    
    def clear_completed_uploads(self):
        """Clear completed uploads from memory."""
        completed_ids = [
            file_id for file_id, progress in self.uploads.items()
            if progress.status in [FileStatus.COMPLETED, FileStatus.FAILED, FileStatus.CANCELLED]
        ]
        for file_id in completed_ids:
            del self.uploads[file_id]
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        extension = Path(filename).suffix.lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
            '.gz': 'application/gzip',
        }
        return mime_types.get(extension, 'application/octet-stream')


# Global file service instance
file_service = FileService()