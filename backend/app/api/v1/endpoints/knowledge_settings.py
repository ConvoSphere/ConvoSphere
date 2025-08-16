from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.security import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.services.knowledge_settings_service import KnowledgeSettingsService
from backend.app.schemas.knowledge_settings import KnowledgeBaseSettingsModel

router = APIRouter()


@router.get("/settings")
async def get_knowledge_settings(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> KnowledgeBaseSettingsModel:
	service = KnowledgeSettingsService(db)
	return service.get_settings()


@router.put("/settings")
async def update_knowledge_settings(
	payload: KnowledgeBaseSettingsModel,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> KnowledgeBaseSettingsModel:
	try:
		service = KnowledgeSettingsService(db)
		return service.update_settings(payload)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Invalid settings: {e}")