"""
RAG (Retrieval-Augmented Generation) API endpoints.

This module provides API endpoints for advanced RAG functionality including
configuration management, retrieval, and metrics.
"""

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from backend.app.core.exceptions import AIError, ValidationError
from backend.app.schemas.rag import (
    RAGConfigCreate,
    RAGConfigList,
    RAGConfigResponse,
    RAGConfigUpdate,
    RAGMetrics,
    RAGRequest,
    RAGResponse,
)
from backend.app.services.rag_service import rag_service

router = APIRouter()


@router.post("/retrieve", response_model=RAGResponse)
async def retrieve_rag(
    request: RAGRequest,
) -> RAGResponse:
    """
    Perform RAG retrieval with advanced features.

    Args:
        request: RAG retrieval request

    Returns:
        RAG response with retrieved results
    """
    try:
        response = await rag_service.retrieve(request)
        logger.info(f"RAG retrieval completed for query: {request.query[:50]}...")
        return response
    except (ValidationError, AIError) as e:
        logger.error(f"RAG retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in RAG retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/configs", response_model=RAGConfigResponse)
async def create_rag_config(
    config_request: RAGConfigCreate,
) -> RAGConfigResponse:
    """
    Create new RAG configuration.

    Args:
        config_request: RAG configuration creation request

    Returns:
        Created RAG configuration
    """
    try:
        config_id = await rag_service.create_config(config_request.config)

        return RAGConfigResponse(
            id=config_id,
            name=config_request.name,
            description=config_request.description,
            config=config_request.config,
            created_at=config_request.config.created_at,
            updated_at=config_request.config.updated_at,
        )
    except Exception as e:
        logger.error(f"Failed to create RAG config: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create RAG configuration",
        )


@router.get("/configs", response_model=RAGConfigList)
async def list_rag_configs(
    skip: int = Query(0, ge=0, description="Number of configurations to skip"),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of configurations to return",
    ),
) -> RAGConfigList:
    """
    List RAG configurations.

    Args:
        skip: Number of configurations to skip
        limit: Maximum number of configurations to return

    Returns:
        List of RAG configurations
    """
    try:
        configs = await rag_service.list_configs()

        # Apply pagination
        total = len(configs)
        paginated_configs = configs[skip : skip + limit]

        config_responses = []
        for config_id, config in paginated_configs:
            config_response = RAGConfigResponse(
                id=config_id,
                name=config.name,
                description=config.description,
                config=config,
                created_at=config.created_at,
                updated_at=config.updated_at,
            )
            config_responses.append(config_response)

        return RAGConfigList(
            configs=config_responses,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Failed to list RAG configs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list RAG configurations")


@router.get("/configs/{config_id}", response_model=RAGConfigResponse)
async def get_rag_config(
    config_id: str,
) -> RAGConfigResponse:
    """
    Get RAG configuration by ID.

    Args:
        config_id: Configuration ID

    Returns:
        RAG configuration
    """
    try:
        configs = await rag_service.list_configs()
        config = None

        for cid, cfg in configs:
            if cid == config_id:
                config = cfg
                break

        if not config:
            raise HTTPException(status_code=404, detail="RAG configuration not found")

        return RAGConfigResponse(
            id=config_id,
            name=config.name,
            description=config.description,
            config=config,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get RAG config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get RAG configuration")


@router.put("/configs/{config_id}", response_model=RAGConfigResponse)
async def update_rag_config(
    config_id: str,
    config_update: RAGConfigUpdate,
) -> RAGConfigResponse:
    """
    Update RAG configuration.

    Args:
        config_id: Configuration ID
        config_update: Configuration update request

    Returns:
        Updated RAG configuration
    """
    try:
        # Get existing config
        configs = await rag_service.list_configs()
        existing_config = None

        for cid, cfg in configs:
            if cid == config_id:
                existing_config = cfg
                break

        if not existing_config:
            raise HTTPException(status_code=404, detail="RAG configuration not found")

        # Update config
        if config_update.name is not None:
            existing_config.name = config_update.name
        if config_update.description is not None:
            existing_config.description = config_update.description
        if config_update.config is not None:
            existing_config = config_update.config

        existing_config.updated_at = existing_config.updated_at

        # Save updated config
        success = await rag_service.update_config(config_id, existing_config)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update RAG configuration",
            )

        return RAGConfigResponse(
            id=config_id,
            name=existing_config.name,
            description=existing_config.description,
            config=existing_config,
            created_at=existing_config.created_at,
            updated_at=existing_config.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update RAG config: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update RAG configuration",
        )


@router.delete("/configs/{config_id}")
async def delete_rag_config(
    config_id: str,
) -> dict:
    """
    Delete RAG configuration.

    Args:
        config_id: Configuration ID

    Returns:
        Success message
    """
    try:
        success = await rag_service.delete_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="RAG configuration not found")

        return {"message": "RAG configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete RAG config: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete RAG configuration",
        )


@router.get("/metrics", response_model=RAGMetrics)
async def get_rag_metrics() -> RAGMetrics:
    """
    Get RAG performance metrics.

    Returns:
        RAG metrics
    """
    try:
        return await rag_service.get_metrics()
    except Exception as e:
        logger.error(f"Failed to get RAG metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get RAG metrics")


@router.post("/health")
async def rag_health_check() -> dict:
    """
    Check RAG service health.

    Returns:
        Health status
    """
    try:
        # Check if RAG service is initialized
        metrics = await rag_service.get_metrics()

        return {
            "status": "healthy",
            "service": "rag",
            "total_requests": metrics.total_requests,
            "success_rate": metrics.successful_requests
            / max(metrics.total_requests, 1),
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "rag",
            "error": str(e),
        }
