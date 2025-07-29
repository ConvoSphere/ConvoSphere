"""
Advanced search API endpoints.

This module provides REST API endpoints for:
- Advanced document search with multiple search types
- Search suggestions and autocomplete
- Search analytics and trending
- Faceted search capabilities
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.core.caching import cache
from backend.app.core.rate_limiting import rate_limit_search
from backend.app.monitoring.performance_monitor import monitor_performance
from backend.app.services.search.advanced_search import (
    get_advanced_search_service,
    SearchType,
    SearchFilter,
    SearchFacet
)
from backend.app.models.user import User

router = APIRouter()


@router.post("/search")
@rate_limit_search
@cache(ttl=60, key_prefix="search")
@monitor_performance
async def advanced_search(
    query: str = Body(...),
    search_type: str = Body("hybrid"),
    filters: Optional[List[Dict[str, Any]]] = Body(None),
    facets: Optional[List[Dict[str, Any]]] = Body(None),
    sort_by: str = Body("relevance"),
    sort_order: str = Body("desc"),
    page: int = Body(1, ge=1),
    page_size: int = Body(20, ge=1, le=100),
    include_highlights: bool = Body(True),
    include_facets: bool = Body(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform advanced search with multiple search types."""
    try:
        search_service = get_advanced_search_service(db)
        
        # Convert search type
        try:
            search_type_enum = SearchType(search_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid search type: {search_type}")
        
        # Convert filters
        search_filters = []
        if filters:
            for filter_data in filters:
                search_filters.append(SearchFilter(
                    field=filter_data["field"],
                    operator=filter_data["operator"],
                    value=filter_data["value"],
                    boost=filter_data.get("boost", 1.0)
                ))
        
        # Convert facets
        search_facets = []
        if facets:
            for facet_data in facets:
                search_facets.append(SearchFacet(
                    field=facet_data["field"],
                    size=facet_data.get("size", 10),
                    min_count=facet_data.get("min_count", 1)
                ))
        
        # Perform search
        result = await search_service.search(
            query=query,
            user_id=str(current_user.id),
            search_type=search_type_enum,
            filters=search_filters,
            facets=search_facets,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            include_highlights=include_highlights,
            include_facets=include_facets
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search/suggestions")
@cache(ttl=300, key_prefix="search_suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get search suggestions based on query."""
    try:
        search_service = get_advanced_search_service(db)
        
        suggestions = await search_service.get_search_suggestions(
            query=query,
            user_id=str(current_user.id),
            limit=limit
        )
        
        return [
            {
                "term": suggestion.term,
                "frequency": suggestion.frequency,
                "score": suggestion.score,
                "type": suggestion.type
            }
            for suggestion in suggestions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.get("/search/analytics")
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get search analytics for user."""
    try:
        search_service = get_advanced_search_service(db)
        
        analytics = await search_service.get_search_analytics(
            user_id=str(current_user.id),
            days=days
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.post("/search/full-text")
@rate_limit_search
@monitor_performance
async def full_text_search(
    query: str = Body(...),
    filters: Optional[List[Dict[str, Any]]] = Body(None),
    sort_by: str = Body("relevance"),
    sort_order: str = Body("desc"),
    page: int = Body(1, ge=1),
    page_size: int = Body(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform full-text search."""
    try:
        search_service = get_advanced_search_service(db)
        
        # Convert filters
        search_filters = []
        if filters:
            for filter_data in filters:
                search_filters.append(SearchFilter(
                    field=filter_data["field"],
                    operator=filter_data["operator"],
                    value=filter_data["value"]
                ))
        
        # Perform full-text search
        result = await search_service.search(
            query=query,
            user_id=str(current_user.id),
            search_type=SearchType.FULL_TEXT,
            filters=search_filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full-text search failed: {str(e)}")


@router.post("/search/semantic")
@rate_limit_search
@monitor_performance
async def semantic_search(
    query: str = Body(...),
    filters: Optional[List[Dict[str, Any]]] = Body(None),
    sort_by: str = Body("relevance"),
    sort_order: str = Body("desc"),
    page: int = Body(1, ge=1),
    page_size: int = Body(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform semantic search using embeddings."""
    try:
        search_service = get_advanced_search_service(db)
        
        # Convert filters
        search_filters = []
        if filters:
            for filter_data in filters:
                search_filters.append(SearchFilter(
                    field=filter_data["field"],
                    operator=filter_data["operator"],
                    value=filter_data["value"]
                ))
        
        # Perform semantic search
        result = await search_service.search(
            query=query,
            user_id=str(current_user.id),
            search_type=SearchType.SEMANTIC,
            filters=search_filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


@router.post("/search/faceted")
@rate_limit_search
@monitor_performance
async def faceted_search(
    query: str = Body(...),
    facets: List[Dict[str, Any]] = Body(...),
    filters: Optional[List[Dict[str, Any]]] = Body(None),
    sort_by: str = Body("relevance"),
    sort_order: str = Body("desc"),
    page: int = Body(1, ge=1),
    page_size: int = Body(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform faceted search with aggregations."""
    try:
        search_service = get_advanced_search_service(db)
        
        # Convert filters
        search_filters = []
        if filters:
            for filter_data in filters:
                search_filters.append(SearchFilter(
                    field=filter_data["field"],
                    operator=filter_data["operator"],
                    value=filter_data["value"]
                ))
        
        # Convert facets
        search_facets = []
        for facet_data in facets:
            search_facets.append(SearchFacet(
                field=facet_data["field"],
                size=facet_data.get("size", 10),
                min_count=facet_data.get("min_count", 1)
            ))
        
        # Perform faceted search
        result = await search_service.search(
            query=query,
            user_id=str(current_user.id),
            search_type=SearchType.FACETED,
            filters=search_filters,
            facets=search_facets,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            include_facets=True
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Faceted search failed: {str(e)}")


@router.post("/search/fuzzy")
@rate_limit_search
@monitor_performance
async def fuzzy_search(
    query: str = Body(...),
    filters: Optional[List[Dict[str, Any]]] = Body(None),
    sort_by: str = Body("relevance"),
    sort_order: str = Body("desc"),
    page: int = Body(1, ge=1),
    page_size: int = Body(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform fuzzy search with typo tolerance."""
    try:
        search_service = get_advanced_search_service(db)
        
        # Convert filters
        search_filters = []
        if filters:
            for filter_data in filters:
                search_filters.append(SearchFilter(
                    field=filter_data["field"],
                    operator=filter_data["operator"],
                    value=filter_data["value"]
                ))
        
        # Perform fuzzy search
        result = await search_service.search(
            query=query,
            user_id=str(current_user.id),
            search_type=SearchType.FUZZY,
            filters=search_filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fuzzy search failed: {str(e)}")


@router.get("/search/trending")
@cache(ttl=3600, key_prefix="search_trending")
async def get_trending_searches(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get trending search terms."""
    try:
        search_service = get_advanced_search_service(db)
        
        analytics = await search_service.get_search_analytics(
            user_id=str(current_user.id),
            days=days
        )
        
        # Get trending searches from analytics
        trending = analytics.get("popular_queries", [])[:limit]
        
        return trending
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending searches: {str(e)}")


@router.get("/search/autocomplete")
@cache(ttl=300, key_prefix="search_autocomplete")
async def autocomplete_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Get autocomplete suggestions for search."""
    try:
        search_service = get_advanced_search_service(db)
        
        suggestions = await search_service.get_search_suggestions(
            query=query,
            user_id=str(current_user.id),
            limit=limit
        )
        
        # Return just the terms for autocomplete
        return [suggestion.term for suggestion in suggestions]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get autocomplete: {str(e)}")
