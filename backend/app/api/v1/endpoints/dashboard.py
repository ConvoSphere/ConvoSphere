from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.app.api.v1.endpoints.auth import get_current_active_user  # assuming available

router = APIRouter()

class GridPosition(BaseModel):
	id: str
	x: int
	y: int
	width: int
	height: int

class WidgetConfig(BaseModel):
	id: str
	type: str
	title: str
	description: str | None = None
	size: str
	position: Dict[str, int]
	settings: Dict[str, Any]
	isVisible: bool
	isCollapsed: bool
	refreshInterval: int | None = None
	lastRefresh: str | None = None

class DashboardStateDTO(BaseModel):
	widgets: List[WidgetConfig]
	layout: List[GridPosition]

# Simple in-memory store as fallback (can be replaced by DB service)
_user_dashboards: Dict[str, DashboardStateDTO] = {}

@router.get("/me/dashboard", response_model=DashboardStateDTO)
def get_my_dashboard(current_user=Depends(get_current_active_user)):
	user_id = str(current_user.id)
	if user_id not in _user_dashboards:
		return DashboardStateDTO(widgets=[], layout=[])
	return _user_dashboards[user_id]

@router.put("/me/dashboard")
def save_my_dashboard(state: DashboardStateDTO, current_user=Depends(get_current_active_user)):
	user_id = str(current_user.id)
	_user_dashboards[user_id] = state
	return {"status": "ok"}