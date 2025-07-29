"""
Optimized pagination utilities.

This module provides advanced pagination capabilities including:
- Cursor-based pagination for better performance
- Offset-based pagination with optimizations
- Pagination metadata and navigation
- Performance monitoring for pagination
"""

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

T = TypeVar("T")


class PaginationType(Enum):
    """Types of pagination."""

    OFFSET = "offset"
    CURSOR = "cursor"
    KEYSET = "keyset"


@dataclass
class PaginationParams:
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20
    max_page_size: int = 100
    cursor: str | None = None
    sort_by: str = "id"
    sort_order: str = "desc"
    include_total: bool = True


@dataclass
class PaginationMetadata:
    """Pagination metadata."""

    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    next_cursor: str | None = None
    previous_cursor: str | None = None
    first_cursor: str | None = None
    last_cursor: str | None = None


@dataclass
class PaginatedResult(Generic[T]):
    """Paginated result with data and metadata."""

    items: list[T]
    metadata: PaginationMetadata
    performance_metrics: dict[str, Any]


class CursorPagination:
    """Cursor-based pagination for optimal performance."""

    def __init__(self, db: Session):
        self.db = db

    async def paginate_with_cursor(
        self,
        query: Select,
        pagination_params: PaginationParams,
        cursor_field: str = "id",
        cursor_value: str | None = None,
    ) -> PaginatedResult:
        """
        Paginate query using cursor-based pagination.

        Args:
            query: SQLAlchemy query
            pagination_params: Pagination parameters
            cursor_field: Field to use for cursor
            cursor_value: Current cursor value

        Returns:
            Paginated result
        """
        start_time = datetime.utcnow()

        # Apply cursor filter
        if cursor_value:
            if pagination_params.sort_order == "desc":
                query = query.where(
                    getattr(query.column_descriptions[0]["type"], cursor_field)
                    < cursor_value
                )
            else:
                query = query.where(
                    getattr(query.column_descriptions[0]["type"], cursor_field)
                    > cursor_value
                )

        # Apply sorting
        sort_column = getattr(
            query.column_descriptions[0]["type"], pagination_params.sort_by
        )
        if pagination_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply limit
        limit = min(pagination_params.page_size, pagination_params.max_page_size)
        query = query.limit(limit + 1)  # +1 to check if there are more items

        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()

        # Check if there are more items
        has_next = len(items) > limit
        if has_next:
            items = items[:-1]  # Remove the extra item

        # Generate cursors
        cursors = self._generate_cursors(items, cursor_field)

        # Calculate performance metrics
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        metadata = PaginationMetadata(
            current_page=1,  # Cursor pagination doesn't use page numbers
            page_size=len(items),
            total_items=-1,  # Not available in cursor pagination
            total_pages=-1,  # Not available in cursor pagination
            has_next=has_next,
            has_previous=cursor_value is not None,
            next_cursor=cursors.get("next") if has_next else None,
            previous_cursor=cursor_value,
            first_cursor=cursors.get("first"),
            last_cursor=cursors.get("last"),
        )

        performance_metrics = {
            "execution_time": execution_time,
            "pagination_type": "cursor",
            "items_returned": len(items),
        }

        return PaginatedResult(
            items=items, metadata=metadata, performance_metrics=performance_metrics
        )

    def _generate_cursors(self, items: list[Any], cursor_field: str) -> dict[str, str]:
        """Generate cursors for items."""
        cursors = {}

        if items:
            first_item = items[0]
            last_item = items[-1]

            cursors["first"] = str(getattr(first_item, cursor_field))
            cursors["last"] = str(getattr(last_item, cursor_field))

            if len(items) > 1:
                cursors["next"] = str(getattr(last_item, cursor_field))

        return cursors


class OffsetPagination:
    """Optimized offset-based pagination."""

    def __init__(self, db: Session):
        self.db = db

    async def paginate_with_offset(
        self, query: Select, pagination_params: PaginationParams
    ) -> PaginatedResult:
        """
        Paginate query using offset-based pagination with optimizations.

        Args:
            query: SQLAlchemy query
            pagination_params: Pagination parameters

        Returns:
            Paginated result
        """
        start_time = datetime.utcnow()

        # Apply sorting
        sort_column = getattr(
            query.column_descriptions[0]["type"], pagination_params.sort_by
        )
        if pagination_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Calculate offset and limit
        page_size = min(pagination_params.page_size, pagination_params.max_page_size)
        offset = (pagination_params.page - 1) * page_size

        # Get total count if requested
        total_items = -1
        if pagination_params.include_total:
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await self.db.execute(count_query)
            total_items = count_result.scalar()

        # Apply pagination
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()

        # Calculate metadata
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
        has_next = pagination_params.page < total_pages
        has_previous = pagination_params.page > 1

        metadata = PaginationMetadata(
            current_page=pagination_params.page,
            page_size=len(items),
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
            next_cursor=None,
            previous_cursor=None,
            first_cursor=None,
            last_cursor=None,
        )

        # Calculate performance metrics
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        performance_metrics = {
            "execution_time": execution_time,
            "pagination_type": "offset",
            "items_returned": len(items),
            "total_items": total_items,
            "offset": offset,
        }

        return PaginatedResult(
            items=items, metadata=metadata, performance_metrics=performance_metrics
        )


class KeysetPagination:
    """Keyset pagination for complex sorting scenarios."""

    def __init__(self, db: Session):
        self.db = db

    async def paginate_with_keyset(
        self,
        query: Select,
        pagination_params: PaginationParams,
        keyset_fields: list[str],
        keyset_values: list[Any] | None = None,
    ) -> PaginatedResult:
        """
        Paginate query using keyset pagination.

        Args:
            query: SQLAlchemy query
            pagination_params: Pagination parameters
            keyset_fields: Fields to use for keyset
            keyset_values: Current keyset values

        Returns:
            Paginated result
        """
        start_time = datetime.utcnow()

        # Apply keyset filter
        if keyset_values and len(keyset_values) == len(keyset_fields):
            keyset_conditions = []
            for field, value in zip(keyset_fields, keyset_values, strict=False):
                field_column = getattr(query.column_descriptions[0]["type"], field)
                if pagination_params.sort_order == "desc":
                    keyset_conditions.append(field_column < value)
                else:
                    keyset_conditions.append(field_column > value)

            if keyset_conditions:
                query = query.where(*keyset_conditions)

        # Apply sorting
        sort_columns = []
        for field in keyset_fields:
            sort_column = getattr(query.column_descriptions[0]["type"], field)
            if pagination_params.sort_order == "desc":
                sort_columns.append(desc(sort_column))
            else:
                sort_columns.append(asc(sort_column))

        query = query.order_by(*sort_columns)

        # Apply limit
        limit = min(pagination_params.page_size, pagination_params.max_page_size)
        query = query.limit(limit + 1)

        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()

        # Check if there are more items
        has_next = len(items) > limit
        if has_next:
            items = items[:-1]

        # Generate keyset values
        keyset_cursors = self._generate_keyset_cursors(items, keyset_fields)

        # Calculate performance metrics
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        metadata = PaginationMetadata(
            current_page=1,
            page_size=len(items),
            total_items=-1,
            total_pages=-1,
            has_next=has_next,
            has_previous=keyset_values is not None,
            next_cursor=keyset_cursors.get("next"),
            previous_cursor=str(keyset_values) if keyset_values else None,
            first_cursor=keyset_cursors.get("first"),
            last_cursor=keyset_cursors.get("last"),
        )

        performance_metrics = {
            "execution_time": execution_time,
            "pagination_type": "keyset",
            "items_returned": len(items),
            "keyset_fields": keyset_fields,
        }

        return PaginatedResult(
            items=items, metadata=metadata, performance_metrics=performance_metrics
        )

    def _generate_keyset_cursors(
        self, items: list[Any], keyset_fields: list[str]
    ) -> dict[str, str]:
        """Generate keyset cursors for items."""
        cursors = {}

        if items:
            first_item = items[0]
            last_item = items[-1]

            first_values = [str(getattr(first_item, field)) for field in keyset_fields]
            last_values = [str(getattr(last_item, field)) for field in keyset_fields]

            cursors["first"] = "|".join(first_values)
            cursors["last"] = "|".join(last_values)

            if len(items) > 1:
                cursors["next"] = "|".join(last_values)

        return cursors


class PaginationOptimizer:
    """Optimizer for pagination performance."""

    def __init__(self, db: Session):
        self.db = db
        self.cursor_pagination = CursorPagination(db)
        self.offset_pagination = OffsetPagination(db)
        self.keyset_pagination = KeysetPagination(db)

    def choose_pagination_strategy(
        self,
        query: Select,
        pagination_params: PaginationParams,
        estimated_total: int | None = None,
    ) -> PaginationType:
        """
        Choose the best pagination strategy based on query and parameters.

        Args:
            query: SQLAlchemy query
            pagination_params: Pagination parameters
            estimated_total: Estimated total number of items

        Returns:
            Recommended pagination type
        """
        # Use cursor pagination for large datasets
        if estimated_total and estimated_total > 10000:
            return PaginationType.CURSOR

        # Use keyset pagination for complex sorting
        if pagination_params.sort_by not in {"id", "created_at"}:
            return PaginationType.KEYSET

        # Use offset pagination for small datasets with total count needed
        if pagination_params.include_total and (
            not estimated_total or estimated_total < 1000
        ):
            return PaginationType.OFFSET

        # Default to cursor pagination for better performance
        return PaginationType.CURSOR

    async def paginate(
        self,
        query: Select,
        pagination_params: PaginationParams,
        strategy: PaginationType | None = None,
        **kwargs,
    ) -> PaginatedResult:
        """
        Paginate query using the best strategy.

        Args:
            query: SQLAlchemy query
            pagination_params: Pagination parameters
            strategy: Specific pagination strategy to use
            **kwargs: Additional arguments for specific pagination types

        Returns:
            Paginated result
        """
        if strategy is None:
            strategy = self.choose_pagination_strategy(query, pagination_params)

        if strategy == PaginationType.CURSOR:
            return await self.cursor_pagination.paginate_with_cursor(
                query, pagination_params, **kwargs
            )
        if strategy == PaginationType.KEYSET:
            return await self.keyset_pagination.paginate_with_keyset(
                query, pagination_params, **kwargs
            )
        return await self.offset_pagination.paginate_with_offset(
            query, pagination_params
        )


def create_pagination_links(
    base_url: str,
    metadata: PaginationMetadata,
    additional_params: dict[str, Any] = None,
) -> dict[str, str]:
    """Create pagination links for API responses."""
    links = {}
    params = additional_params or {}

    # First page
    if metadata.first_cursor:
        first_params = {**params, "cursor": metadata.first_cursor}
        links["first"] = (
            f"{base_url}?{'&'.join(f'{k}={v}' for k, v in first_params.items())}"
        )

    # Previous page
    if metadata.has_previous and metadata.previous_cursor:
        prev_params = {**params, "cursor": metadata.previous_cursor}
        links["prev"] = (
            f"{base_url}?{'&'.join(f'{k}={v}' for k, v in prev_params.items())}"
        )

    # Next page
    if metadata.has_next and metadata.next_cursor:
        next_params = {**params, "cursor": metadata.next_cursor}
        links["next"] = (
            f"{base_url}?{'&'.join(f'{k}={v}' for k, v in next_params.items())}"
        )

    # Last page
    if metadata.last_cursor:
        last_params = {**params, "cursor": metadata.last_cursor}
        links["last"] = (
            f"{base_url}?{'&'.join(f'{k}={v}' for k, v in last_params.items())}"
        )

    return links


def decode_cursor(cursor: str) -> list[Any]:
    """Decode cursor string to values."""
    if not cursor:
        return []

    # Handle keyset cursors (pipe-separated)
    if "|" in cursor:
        return cursor.split("|")

    # Handle single value cursors
    return [cursor]


def encode_cursor(values: list[Any]) -> str:
    """Encode values to cursor string."""
    if not values:
        return ""

    # Handle multiple values (keyset)
    if len(values) > 1:
        return "|".join(str(v) for v in values)

    # Handle single value
    return str(values[0])
