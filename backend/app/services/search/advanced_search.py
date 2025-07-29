"""
Advanced search service with full-text search, semantic search, and extended filtering.

This module provides comprehensive search functionality including:
- Full-text search with relevance scoring
- Semantic search using embeddings
- Advanced filtering and faceted search
- Search suggestions and autocomplete
- Search analytics and trending
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from backend.app.models.knowledge import Document, DocumentChunk, SearchQuery, Tag
from backend.app.services.weaviate_service import WeaviateService
from backend.app.services.ai_service import AIService
from loguru import logger
from backend.app.core.config import get_settings




class SearchType(Enum):
    """Types of search operations."""
    FULL_TEXT = "full_text"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    FACETED = "faceted"
    FUZZY = "fuzzy"


class SearchOperator(Enum):
    """Search operators for advanced queries."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    PHRASE = "PHRASE"
    WILDCARD = "WILDCARD"
    RANGE = "RANGE"


@dataclass
class SearchFilter:
    """Search filter configuration."""
    field: str
    operator: str
    value: Any
    boost: float = 1.0


@dataclass
class SearchFacet:
    """Search facet configuration."""
    field: str
    size: int = 10
    min_count: int = 1


@dataclass
class SearchResult:
    """Search result with metadata."""
    document_id: str
    chunk_id: str
    content: str
    score: float
    highlights: List[str]
    metadata: Dict[str, Any]
    document_info: Dict[str, Any]


@dataclass
class SearchSuggestion:
    """Search suggestion."""
    term: str
    frequency: int
    score: float
    type: str  # "term", "phrase", "tag"


class AdvancedSearchService:
    """Advanced search service with multiple search capabilities."""
    
    def __init__(self, db: Session):
        self.db = db
        self.weaviate_service = WeaviateService()
        self.ai_service = AIService()
        self.settings = get_settings()
        
        # Search configuration
        self.max_results = 1000
        self.min_score_threshold = 0.1
        self.fuzzy_distance = 2
        self.semantic_weight = 0.7
        self.text_weight = 0.3
    
    async def search(
        self,
        query: str,
        user_id: str,
        search_type: SearchType = SearchType.HYBRID,
        filters: List[SearchFilter] = None,
        facets: List[SearchFacet] = None,
        sort_by: str = "relevance",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
        include_highlights: bool = True,
        include_facets: bool = True
    ) -> Dict[str, Any]:
        """
        Perform advanced search with multiple search types.
        
        Args:
            query: Search query
            user_id: User ID for access control
            search_type: Type of search to perform
            filters: List of search filters
            facets: List of facets to compute
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            page: Page number
            sort_order: Sort order
            page: Page number
            page_size: Results per page
            include_highlights: Whether to include highlights
            include_facets: Whether to include facets
            
        Returns:
            Search results with metadata
        """
        try:
            # Log search query
            await self._log_search_query(query, user_id, search_type)
            
            # Parse and validate query
            parsed_query = self._parse_query(query)
            
            # Apply filters
            applied_filters = self._apply_filters(filters or [])
            
            # Perform search based on type
            if search_type == SearchType.FULL_TEXT:
                results = await self._full_text_search(parsed_query, applied_filters, user_id)
            elif search_type == SearchType.SEMANTIC:
                results = await self._semantic_search(parsed_query, applied_filters, user_id)
            elif search_type == SearchType.HYBRID:
                results = await self._hybrid_search(parsed_query, applied_filters, user_id)
            elif search_type == SearchType.FACETED:
                results = await self._faceted_search(parsed_query, applied_filters, user_id, facets)
            elif search_type == SearchType.FUZZY:
                results = await self._fuzzy_search(parsed_query, applied_filters, user_id)
            else:
                raise ValueError(f"Unsupported search type: {search_type}")
            
            # Apply sorting
            results = self._sort_results(results, sort_by, sort_order)
            
            # Apply pagination
            total = len(results)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_results = results[start_idx:end_idx]
            
            # Add highlights if requested
            if include_highlights:
                paginated_results = await self._add_highlights(paginated_results, parsed_query)
            
            # Compute facets if requested
            facet_results = {}
            if include_facets and facets:
                facet_results = await self._compute_facets(results, facets)
            
            # Format results
            formatted_results = [
                {
                    "document_id": result.document_id,
                    "chunk_id": result.chunk_id,
                    "content": result.content,
                    "score": result.score,
                    "highlights": result.highlights,
                    "metadata": result.metadata,
                    "document_info": result.document_info
                }
                for result in paginated_results
            ]
            
            return {
                "results": formatted_results,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "facets": facet_results,
                "search_type": search_type.value,
                "query": query,
                "filters_applied": [f.field for f in filters or []]
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse search query into structured format."""
        parsed = {
            "original": query,
            "terms": [],
            "phrases": [],
            "operators": [],
            "filters": []
        }
        
        # Extract phrases (quoted text)
        phrase_pattern = r'"([^"]*)"'
        phrases = re.findall(phrase_pattern, query)
        parsed["phrases"] = phrases
        
        # Remove phrases from query for term extraction
        term_query = re.sub(phrase_pattern, "", query)
        
        # Extract terms
        terms = re.findall(r'\b\w+\b', term_query.lower())
        parsed["terms"] = [term for term in terms if len(term) > 2]
        
        # Extract operators
        operators = re.findall(r'\b(AND|OR|NOT)\b', query.upper())
        parsed["operators"] = operators
        
        return parsed
    
    def _apply_filters(self, filters: List[SearchFilter]) -> Dict[str, Any]:
        """Apply search filters to query."""
        applied_filters = {}
        
        for filter_item in filters:
            if filter_item.operator == "equals":
                applied_filters[filter_item.field] = filter_item.value
            elif filter_item.operator == "range":
                applied_filters[f"{filter_item.field}_range"] = filter_item.value
            elif filter_item.operator == "in":
                applied_filters[f"{filter_item.field}_in"] = filter_item.value
            elif filter_item.operator == "exists":
                applied_filters[f"{filter_item.field}_exists"] = True
        
        return applied_filters
    
    async def _full_text_search(
        self,
        parsed_query: Dict[str, Any],
        filters: Dict[str, Any],
        user_id: str
    ) -> List[SearchResult]:
        """Perform full-text search using database."""
        results = []
        
        # Build SQL query
        query = self.db.query(DocumentChunk).join(Document).filter(
            Document.user_id == user_id
        )
        
        # Add text search conditions
        search_conditions = []
        for term in parsed_query["terms"]:
            search_conditions.append(DocumentChunk.content.ilike(f"%{term}%"))
        
        for phrase in parsed_query["phrases"]:
            search_conditions.append(DocumentChunk.content.ilike(f"%{phrase}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Apply filters
        query = self._apply_sql_filters(query, filters)
        
        # Execute query
        chunks = query.limit(self.max_results).all()
        
        # Convert to search results
        for chunk in chunks:
            score = self._calculate_text_score(chunk, parsed_query)
            if score >= self.min_score_threshold:
                result = SearchResult(
                    document_id=str(chunk.document_id),
                    chunk_id=str(chunk.id),
                    content=chunk.content,
                    score=score,
                    highlights=[],
                    metadata={
                        "chunk_index": chunk.chunk_index,
                        "chunk_type": chunk.chunk_type,
                        "page_number": chunk.page_number,
                        "section_title": chunk.section_title
                    },
                    document_info=self._get_document_info(chunk.document)
                )
                results.append(result)
        
        return results
    
    async def _semantic_search(
        self,
        parsed_query: Dict[str, Any],
        filters: Dict[str, Any],
        user_id: str
    ) -> List[SearchResult]:
        """Perform semantic search using embeddings."""
        try:
            # Generate query embedding
            query_text = " ".join(parsed_query["terms"] + parsed_query["phrases"])
            query_embedding = await self.ai_service.generate_embedding(query_text)
            
            if not query_embedding:
                return []
            
            # Search in Weaviate
            weaviate_results = self.weaviate_service.search_similar(
                query_embedding=query_embedding,
                limit=self.max_results,
                filters=self._convert_filters_for_weaviate(filters, user_id)
            )
            
            # Convert to search results
            results = []
            for weaviate_result in weaviate_results:
                chunk = self.db.query(DocumentChunk).filter(
                    DocumentChunk.id == weaviate_result["chunk_id"]
                ).first()
                
                if chunk and chunk.document.user_id == user_id:
                    result = SearchResult(
                        document_id=str(chunk.document_id),
                        chunk_id=str(chunk.id),
                        content=chunk.content,
                        score=weaviate_result["score"],
                        highlights=[],
                        metadata={
                            "chunk_index": chunk.chunk_index,
                            "chunk_type": chunk.chunk_type,
                            "page_number": chunk.page_number,
                            "section_title": chunk.section_title
                        },
                        document_info=self._get_document_info(chunk.document)
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _hybrid_search(
        self,
        parsed_query: Dict[str, Any],
        filters: Dict[str, Any],
        user_id: str
    ) -> List[SearchResult]:
        """Perform hybrid search combining text and semantic search."""
        # Run both searches in parallel
        text_results, semantic_results = await asyncio.gather(
            self._full_text_search(parsed_query, filters, user_id),
            self._semantic_search(parsed_query, filters, user_id),
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(text_results, Exception):
            logger.error(f"Text search failed: {text_results}")
            text_results = []
        if isinstance(semantic_results, Exception):
            logger.error(f"Semantic search failed: {semantic_results}")
            semantic_results = []
        
        # Combine results
        combined_results = {}
        
        # Add text results
        for result in text_results:
            key = result.chunk_id
            combined_results[key] = result
            combined_results[key].score *= self.text_weight
        
        # Add semantic results
        for result in semantic_results:
            key = result.chunk_id
            if key in combined_results:
                # Combine scores
                combined_results[key].score += result.score * self.semantic_weight
            else:
                result.score *= self.semantic_weight
                combined_results[key] = result
        
        # Sort by combined score
        results = list(combined_results.values())
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    async def _faceted_search(
        self,
        parsed_query: Dict[str, Any],
        filters: Dict[str, Any],
        user_id: str,
        facets: List[SearchFacet]
    ) -> List[SearchResult]:
        """Perform faceted search with aggregation."""
        # First perform regular search
        results = await self._hybrid_search(parsed_query, filters, user_id)
        
        # Then compute facets
        facet_data = await self._compute_facets(results, facets)
        
        # Add facet information to results
        for result in results:
            result.metadata["facets"] = facet_data
        
        return results
    
    async def _fuzzy_search(
        self,
        parsed_query: Dict[str, Any],
        filters: Dict[str, Any],
        user_id: str
    ) -> List[SearchResult]:
        """Perform fuzzy search with typo tolerance."""
        results = []
        
        # Build fuzzy search conditions
        fuzzy_conditions = []
        for term in parsed_query["terms"]:
            # Use PostgreSQL trigram similarity for fuzzy matching
            fuzzy_conditions.append(
                func.similarity(DocumentChunk.content, term) > 0.3
            )
        
        if fuzzy_conditions:
            query = self.db.query(DocumentChunk).join(Document).filter(
                Document.user_id == user_id,
                or_(*fuzzy_conditions)
            )
            
            # Apply filters
            query = self._apply_sql_filters(query, filters)
            
            # Execute query
            chunks = query.limit(self.max_results).all()
            
            # Convert to search results
            for chunk in chunks:
                score = self._calculate_fuzzy_score(chunk, parsed_query)
                if score >= self.min_score_threshold:
                    result = SearchResult(
                        document_id=str(chunk.document_id),
                        chunk_id=str(chunk.id),
                        content=chunk.content,
                        score=score,
                        highlights=[],
                        metadata={
                            "chunk_index": chunk.chunk_index,
                            "chunk_type": chunk.chunk_type,
                            "page_number": chunk.page_number,
                            "section_title": chunk.section_title
                        },
                        document_info=self._get_document_info(chunk.document)
                    )
                    results.append(result)
        
        return results
    
    def _apply_sql_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to SQL query."""
        for field, value in filters.items():
            if field == "document_type":
                query = query.filter(Document.document_type == value)
            elif field == "author":
                query = query.filter(Document.author.ilike(f"%{value}%"))
            elif field == "language":
                query = query.filter(Document.language == value)
            elif field == "year_range":
                start_year, end_year = value
                query = query.filter(
                    and_(
                        Document.year >= start_year,
                        Document.year <= end_year
                    )
                )
            elif field == "status":
                query = query.filter(Document.status == value)
            elif field == "tags_in":
                query = query.join(Document.tags).filter(Tag.name.in_(value))
        
        return query
    
    def _convert_filters_for_weaviate(self, filters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Convert filters for Weaviate search."""
        weaviate_filters = {
            "user_id": user_id
        }
        
        for field, value in filters.items():
            if field == "document_type":
                weaviate_filters["document_type"] = value
            elif field == "language":
                weaviate_filters["language"] = value
            elif field == "year_range":
                start_year, end_year = value
                weaviate_filters["year"] = {
                    "operator": "Between",
                    "valueDate": [f"{start_year}-01-01T00:00:00Z", f"{end_year}-12-31T23:59:59Z"]
                }
        
        return weaviate_filters
    
    def _calculate_text_score(self, chunk: DocumentChunk, parsed_query: Dict[str, Any]) -> float:
        """Calculate relevance score for text search."""
        score = 0.0
        content_lower = chunk.content.lower()
        
        # Term frequency
        for term in parsed_query["terms"]:
            term_count = content_lower.count(term)
            if term_count > 0:
                score += term_count * 0.1
        
        # Phrase matching (higher weight)
        for phrase in parsed_query["phrases"]:
            if phrase.lower() in content_lower:
                score += 1.0
        
        # Boost by chunk type
        if chunk.chunk_type == "title":
            score *= 2.0
        elif chunk.chunk_type == "heading":
            score *= 1.5
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _calculate_fuzzy_score(self, chunk: DocumentChunk, parsed_query: Dict[str, Any]) -> float:
        """Calculate relevance score for fuzzy search."""
        # Use PostgreSQL trigram similarity
        from sqlalchemy import func
        
        score = 0.0
        for term in parsed_query["terms"]:
            similarity = self.db.query(
                func.similarity(chunk.content, term)
            ).scalar()
            score += similarity
        
        return score
    
    def _sort_results(self, results: List[SearchResult], sort_by: str, sort_order: str) -> List[SearchResult]:
        """Sort search results."""
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "relevance":
            results.sort(key=lambda x: x.score, reverse=reverse)
        elif sort_by == "date":
            results.sort(key=lambda x: x.document_info.get("created_at", ""), reverse=reverse)
        elif sort_by == "title":
            results.sort(key=lambda x: x.document_info.get("title", ""), reverse=reverse)
        elif sort_by == "author":
            results.sort(key=lambda x: x.document_info.get("author", ""), reverse=reverse)
        
        return results
    
    async def _add_highlights(self, results: List[SearchResult], parsed_query: Dict[str, Any]) -> List[SearchResult]:
        """Add highlights to search results."""
        for result in results:
            highlights = []
            content = result.content
            
            # Highlight terms
            for term in parsed_query["terms"]:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                matches = pattern.finditer(content)
                for match in matches:
                    start = max(0, match.start() - 20)
                    end = min(len(content), match.end() + 20)
                    highlight = f"...{content[start:end]}..."
                    highlights.append(highlight)
            
            # Highlight phrases
            for phrase in parsed_query["phrases"]:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                matches = pattern.finditer(content)
                for match in matches:
                    start = max(0, match.start() - 30)
                    end = min(len(content), match.end() + 30)
                    highlight = f"...{content[start:end]}..."
                    highlights.append(highlight)
            
            result.highlights = highlights[:3]  # Limit to 3 highlights
        
        return results
    
    async def _compute_facets(self, results: List[SearchResult], facets: List[SearchFacet]) -> Dict[str, Any]:
        """Compute facets from search results."""
        facet_results = {}
        
        for facet in facets:
            facet_values = {}
            
            for result in results:
                value = result.document_info.get(facet.field)
                if value:
                    if isinstance(value, list):
                        for item in value:
                            facet_values[item] = facet_values.get(item, 0) + 1
                    else:
                        facet_values[value] = facet_values.get(value, 0) + 1
            
            # Sort by frequency and limit
            sorted_facets = sorted(
                facet_values.items(),
                key=lambda x: x[1],
                reverse=True
            )[:facet.size]
            
            # Filter by minimum count
            filtered_facets = [
                {"value": value, "count": count}
                for value, count in sorted_facets
                if count >= facet.min_count
            ]
            
            facet_results[facet.field] = filtered_facets
        
        return facet_results
    
    def _get_document_info(self, document: Document) -> Dict[str, Any]:
        """Get document information for search results."""
        return {
            "title": document.title,
            "description": document.description,
            "author": document.author,
            "document_type": document.document_type,
            "language": document.language,
            "year": document.year,
            "file_type": document.file_type,
            "status": document.status,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "processed_at": document.processed_at.isoformat() if document.processed_at else None,
            "tags": [tag.name for tag in document.tags],
            "keywords": document.keywords
        }
    
    async def _log_search_query(self, query: str, user_id: str, search_type: SearchType):
        """Log search query for analytics."""
        try:
            search_query = SearchQuery(
                user_id=user_id,
                query=query,
                search_type=search_type.value,
                timestamp=datetime.utcnow()
            )
            self.db.add(search_query)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log search query: {e}")
    
    async def get_search_suggestions(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[SearchSuggestion]:
        """Get search suggestions based on query."""
        suggestions = []
        
        # Get popular search terms
        popular_terms = self.db.query(
            SearchQuery.query,
            func.count(SearchQuery.id).label('frequency')
        ).filter(
            SearchQuery.user_id == user_id,
            SearchQuery.query.ilike(f"%{query}%")
        ).group_by(SearchQuery.query).order_by(
            func.count(SearchQuery.id).desc()
        ).limit(limit).all()
        
        for term, frequency in popular_terms:
            suggestions.append(SearchSuggestion(
                term=term,
                frequency=frequency,
                score=frequency * 0.1,
                type="term"
            ))
        
        # Get tag suggestions
        tag_suggestions = self.db.query(Tag).filter(
            Tag.name.ilike(f"%{query}%")
        ).limit(limit).all()
        
        for tag in tag_suggestions:
            suggestions.append(SearchSuggestion(
                term=tag.name,
                frequency=tag.document_count or 0,
                score=tag.document_count or 0,
                type="tag"
            ))
        
        # Sort by score
        suggestions.sort(key=lambda x: x.score, reverse=True)
        
        return suggestions[:limit]
    
    async def get_search_analytics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get search analytics for user."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total searches
        total_searches = self.db.query(SearchQuery).filter(
            SearchQuery.user_id == user_id,
            SearchQuery.timestamp >= start_date
        ).count()
        
        # Search types distribution
        search_types = self.db.query(
            SearchQuery.search_type,
            func.count(SearchQuery.id).label('count')
        ).filter(
            SearchQuery.user_id == user_id,
            SearchQuery.timestamp >= start_date
        ).group_by(SearchQuery.search_type).all()
        
        # Popular queries
        popular_queries = self.db.query(
            SearchQuery.query,
            func.count(SearchQuery.id).label('count')
        ).filter(
            SearchQuery.user_id == user_id,
            SearchQuery.timestamp >= start_date
        ).group_by(SearchQuery.query).order_by(
            func.count(SearchQuery.id).desc()
        ).limit(10).all()
        
        # Daily search trend
        daily_trend = self.db.query(
            func.date(SearchQuery.timestamp).label('date'),
            func.count(SearchQuery.id).label('count')
        ).filter(
            SearchQuery.user_id == user_id,
            SearchQuery.timestamp >= start_date
        ).group_by(
            func.date(SearchQuery.timestamp)
        ).order_by(
            func.date(SearchQuery.timestamp)
        ).all()
        
        return {
            "total_searches": total_searches,
            "search_types": {st.search_type: st.count for st in search_types},
            "popular_queries": [{"query": pq.query, "count": pq.count} for pq in popular_queries],
            "daily_trend": [{"date": dt.date, "count": dt.count} for dt in daily_trend]
        }


# Global search service instance
_search_service: Optional[AdvancedSearchService] = None

def get_advanced_search_service(db: Session) -> AdvancedSearchService:
    """Get or create advanced search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = AdvancedSearchService(db)
    return _search_service