from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.core.config import get_settings
from backend.app.core.security import get_current_user
from backend.app.models.user import User

router = APIRouter()


class KnowledgeBaseSettingsModel(BaseModel):
	chunkSize: int = Field(default=500, ge=100, le=2000)
	chunkOverlap: int = Field(default=50, ge=0, le=500)
	embeddingModel: str = Field(default="text-embedding-ada-002")
	indexType: str = Field(default="hybrid")
	metadataExtraction: bool = Field(default=True)
	autoTagging: bool = Field(default=True)
	searchAlgorithm: str = Field(default="hybrid")
	maxFileSize: int = Field(default=10 * 1024 * 1024, ge=1024 * 1024, le=100 * 1024 * 1024)
	supportedFileTypes: list[str] = Field(default_factory=lambda: [
		"application/pdf",
		"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		"text/plain",
		"text/markdown",
	])
	processingTimeout: int = Field(default=300, ge=60, le=3600)
	batchSize: int = Field(default=10, ge=1, le=100)
	enableCache: bool = Field(default=True)
	cacheExpiry: int = Field(default=3600, ge=60, le=24 * 3600)


# In-memory fallback storage; replace by DB persistence later
_IN_MEMORY_SETTINGS: KnowledgeBaseSettingsModel | None = None


def _get_current_settings() -> KnowledgeBaseSettingsModel:
	global _IN_MEMORY_SETTINGS
	if _IN_MEMORY_SETTINGS is not None:
		return _IN_MEMORY_SETTINGS
	s = get_settings().knowledge_base
	return KnowledgeBaseSettingsModel(
		chunkSize=getattr(s, "chunk_size", 500),
		chunkOverlap=getattr(s, "chunk_overlap", 50),
		embeddingModel=getattr(s, "default_embedding_model", "text-embedding-ada-002"),
		indexType="hybrid",
		metadataExtraction=True,
		autoTagging=True,
		searchAlgorithm="hybrid",
		maxFileSize=getattr(s, "max_file_size", 10 * 1024 * 1024),
		supportedFileTypes=getattr(s, "supported_file_types", []),
		processingTimeout=300,
		batchSize=10,
		enableCache=True,
		cacheExpiry=3600,
	)


@router.get("/settings")
async def get_knowledge_settings(current_user: User = Depends(get_current_user)) -> KnowledgeBaseSettingsModel:
	return _get_current_settings()


@router.put("/settings")
async def update_knowledge_settings(
	payload: KnowledgeBaseSettingsModel,
	current_user: User = Depends(get_current_user),
) -> KnowledgeBaseSettingsModel:
	# Basic validation beyond Pydantic constraints if needed
	try:
		global _IN_MEMORY_SETTINGS
		_IN_MEMORY_SETTINGS = payload
		return _IN_MEMORY_SETTINGS
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Invalid settings: {e}")