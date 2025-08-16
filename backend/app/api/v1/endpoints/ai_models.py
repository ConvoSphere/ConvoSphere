from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.services.ai_models_service import AIModelsService
from backend.app.services.ai_service import get_ai_service

router = APIRouter()


class ModelPerformance(BaseModel):
	latencyMsAvg: float
	tokensPerSecond: float
	successRate: float
	timeframe: str


class ModelUsage(BaseModel):
	totalRequests: int
	totalTokens: int
	averageTokensPerRequest: float
	timeframe: str


class ModelCosts(BaseModel):
	totalCostUsd: float
	inputCostUsd: float
	outputCostUsd: float
	timeframe: str


class AIModelDTO(BaseModel):
	name: str = Field(...)
	provider: str = Field(...)
	model_key: str = Field(...)
	display_name: str = Field(...)
	description: Optional[str] = None
	max_tokens: Optional[int] = None
	cost_per_1k_tokens: Optional[float] = None
	is_active: bool = True
	is_default: bool = False
	is_favorite: bool = False
	capabilities: List[str] = Field(default_factory=list)


@router.get("/", response_model=List[dict])
async def list_models(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	return [m.to_dict() for m in service.list_models()]


@router.get("/{model_id}", response_model=dict)
async def get_model(
	model_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	m = service.get_model(model_id)
	if not m:
		raise HTTPException(status_code=404, detail="Model not found")
	return m.to_dict()


@router.post("/", response_model=dict)
async def create_model(
	payload: AIModelDTO,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	m = service.create_model(payload.dict())
	return m.to_dict()


@router.put("/{model_id}", response_model=dict)
async def update_model(
	model_id: str,
	payload: dict,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	m = service.update_model(model_id, payload)
	if not m:
		raise HTTPException(status_code=404, detail="Model not found")
	return m.to_dict()


@router.delete("/{model_id}")
async def delete_model(
	model_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	ok = service.delete_model(model_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Model not found")
	return {"message": "Model deleted"}


@router.put("/{model_id}/toggle", response_model=dict)
async def toggle_model(
	model_id: str,
	isActive: bool = Body(..., embed=True),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	m = service.toggle_active(model_id, isActive)
	if not m:
		raise HTTPException(status_code=404, detail="Model not found")
	return m.to_dict()


@router.put("/{model_id}/default", response_model=dict)
async def set_default_model(
	model_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	m = service.set_default(model_id)
	if not m:
		raise HTTPException(status_code=404, detail="Model not found")
	return m.to_dict()


class ModelTestRequest(BaseModel):
	prompt: str


@router.post("/{model_id}/test", response_model=dict)
async def test_model(
	model_id: str,
	request: ModelTestRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	# Simple test: call AIService with the specified provider/model_key
	service = AIModelsService(db)
	m = service.get_model(model_id)
	if not m:
		raise HTTPException(status_code=404, detail="Model not found")
	ai = get_ai_service(db)
	# For demo, we won't actually call external provider here; return stub success
	return {
		"id": str(m.id),
		"modelId": str(m.id),
		"prompt": request.prompt,
		"response": "Test response (stub)",
		"responseTime": 0,
		"tokensUsed": 0,
		"cost": 0.0,
		"timestamp": "",
	}


@router.get("/{model_id}/performance", response_model=ModelPerformance)
async def get_model_performance(
	model_id: str,
	timeRange: Optional[str] = Query(None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	# Placeholder - integrate metrics later
	return ModelPerformance(latencyMsAvg=0, tokensPerSecond=0, successRate=1.0, timeframe=timeRange or "")


@router.get("/{model_id}/usage", response_model=ModelUsage)
async def get_model_usage(
	model_id: str,
	timeRange: Optional[str] = Query(None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	return ModelUsage(totalRequests=0, totalTokens=0, averageTokensPerRequest=0, timeframe=timeRange or "")


@router.get("/{model_id}/costs", response_model=ModelCosts)
async def get_model_costs(
	model_id: str,
	timeRange: Optional[str] = Query(None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	return ModelCosts(totalCostUsd=0.0, inputCostUsd=0.0, outputCostUsd=0.0, timeframe=timeRange or "")


@router.get("/providers", response_model=List[str])
async def get_providers(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	ai = get_ai_service(db)
	return ai.get_available_providers()


@router.get("/providers/{provider}/models", response_model=List[str])
async def get_provider_models(
	provider: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	ai = get_ai_service(db)
	return ai.get_available_models(provider)


class ValidateModelRequest(BaseModel):
	name: str
	provider: str
	model_key: str


@router.post("/models/validate", response_model=dict)
async def validate_model(
	request: ValidateModelRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	# Stub validation: ensure provider/model exists in available list
	ai = get_ai_service(db)
	if request.provider not in ai.get_available_providers():
		raise HTTPException(status_code=400, detail="Unknown provider")
	if request.model_key not in ai.get_available_models(request.provider):
		raise HTTPException(status_code=400, detail="Unknown model for provider")
	return {"valid": True}


class CompareModelsRequest(BaseModel):
	modelIds: List[str]


@router.post("/models/compare", response_model=dict)
async def compare_models(
	request: CompareModelsRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	service = AIModelsService(db)
	models = [service.get_model(mid) for mid in request.modelIds]
	if any(m is None for m in models):
		raise HTTPException(status_code=404, detail="One or more models not found")
	# Simple diff output
	differences = []
	keys = ["provider", "model_key", "max_tokens", "cost_per_1k_tokens"]
	for key in keys:
		vals = list({getattr(m, key) for m in models if m})
		if len(vals) > 1:
			differences.append({"key": key, "values": vals})
	return {"differences": differences}


class RecommendationsRequest(BaseModel):
	useCase: str
	requirements: Optional[dict] = None


@router.post("/models/recommendations", response_model=List[dict])
async def get_recommendations(
	request: RecommendationsRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	# Placeholder heuristic
	service = AIModelsService(db)
	models = [m for m in service.list_models() if m.is_active]
	return [m.to_dict() for m in models[:5]]


@router.get("/models/analytics", response_model=dict)
async def get_models_analytics(
	timeRange: Optional[str] = Query(None),
	filters: Optional[str] = Query(None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	# Placeholder analytics aggregation
	service = AIModelsService(db)
	models = service.list_models()
	by_provider = {}
	for m in models:
		by_provider[m.provider] = by_provider.get(m.provider, 0) + 1
	by_model = {m.model_key: 1 for m in models}
	return {"byProvider": by_provider, "byModel": by_model, "timeframe": timeRange or ""}