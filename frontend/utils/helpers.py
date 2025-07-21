"""
Helper functions for the AI Assistant Platform frontend.

This module provides common helper functions used throughout
the frontend application.
"""

import asyncio
import re
import uuid
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any


def format_timestamp(timestamp: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """
    Format timestamp for display.

    Args:
        timestamp: Timestamp to format
        format_str: Format string

    Returns:
        Formatted timestamp string
    """
    if not timestamp:
        return ""
    ts = timestamp
    if isinstance(ts, str):
        try:
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            ts = datetime.fromisoformat(ts)
        except ValueError:
            return ts
    return ts.strftime(format_str)


def format_relative_time(timestamp: datetime) -> str:
    """
    Format timestamp as relative time (e.g., "2 hours ago").

    Args:
        timestamp: Timestamp to format

    Returns:
        Relative time string
    """
    if not timestamp:
        return ""
    ts = timestamp
    if isinstance(ts, str):
        try:
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            ts = datetime.fromisoformat(ts)
        except ValueError:
            return ts
    now = datetime.now()
    diff = now - ts

    if diff.days > 0:
        if diff.days == 1:
            return "Gestern"
        if diff.days < 7:
            return f"vor {diff.days} Tagen"
        return format_timestamp(ts)

    hours = diff.seconds // 3600
    if hours > 0:
        if hours == 1:
            return "vor 1 Stunde"
        return f"vor {hours} Stunden"

    minutes = (diff.seconds % 3600) // 60
    if minutes > 0:
        if minutes == 1:
            return "vor 1 Minute"
        return f"vor {minutes} Minuten"

    return "Gerade eben"


def format_file_size(size_bytes: float) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4()).replace("-", "")[:8]
    return f"{prefix}{unique_id}" if prefix else unique_id


def debounce(delay: float = 0.3):
    """
    Decorator to debounce function calls.

    Args:
        delay: Delay in seconds

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        timer = None

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer

            if timer:
                timer.cancel()

            async def delayed_call():
                await asyncio.sleep(delay)
                await func(*args, **kwargs)

            timer = asyncio.create_task(delayed_call())

        return wrapper

    return decorator


def throttle(delay: float = 0.1):
    """
    Decorator to throttle function calls.

    Args:
        delay: Minimum delay between calls in seconds

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        last_call = 0

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_call
            now = asyncio.get_event_loop().time()

            if now - last_call >= delay:
                last_call = now
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[: 255 - len(ext) - 1] + ("." + ext if ext else "")

    return filename or "unnamed_file"


def extract_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: Filename

    Returns:
        File extension (without dot)
    """
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def is_valid_file_type(filename: str, allowed_extensions: list) -> bool:
    """
    Check if file type is allowed.

    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (with or without dot)

    Returns:
        True if file type is allowed
    """
    extension = extract_file_extension(filename)

    # Normalize extensions (remove dots)
    normalized_allowed = [ext.lower().lstrip(".") for ext in allowed_extensions]

    return extension in normalized_allowed


def parse_query_params(query_string: str) -> dict:
    """
    Parse query string into dictionary.

    Args:
        query_string: Query string

    Returns:
        Dictionary of parameters
    """
    params = {}
    if not query_string:
        return params

    for param in query_string.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params[key] = value

    return params


def build_query_string(params: dict) -> str:
    """
    Build query string from dictionary.

    Args:
        params: Dictionary of parameters

    Returns:
        Query string
    """
    if not params:
        return ""

    return "&".join(
        [f"{key}={value}" for key, value in params.items() if value is not None],
    )


def deep_merge(dict1: dict, dict2: dict) -> dict:
    """
    Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split list into chunks.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(obj: Any, path: str, default: Any = None) -> Any:
    """
    Safely get nested object value.

    Args:
        obj: Object to traverse
        path: Dot-separated path
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    keys = path.split(".")
    current = obj

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            index = int(key)
            if 0 <= index < len(current):
                current = current[index]
            else:
                return default
        else:
            return default

    return current


def format_duration(seconds: int) -> str:
    """
    Format duration in human readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def format_number(value: object) -> str:
    """
    Format a number with thousands separator (German style: 1.234.567,8).
    Args:
        value: The number to format (int or float)
    Returns:
        Formatted number as string
    """
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    if isinstance(value, float):
        return f"{value:,.1f}".replace(",", ".")
    return str(value)
