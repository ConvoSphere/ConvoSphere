from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.app.core.security import get_current_active_user
from backend.app.models.dashboard import UserDashboard
from backend.app.models.base import Base
from backend.app.core.database import get_db  # assuming exists
from sqlalchemy.orm import Session

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

@router.get("/me/dashboard", response_model=DashboardStateDTO)
def get_my_dashboard(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
	user_id = str(current_user.id)
	record = db.query(UserDashboard).filter(UserDashboard.user_id == user_id).first()
	if not record:
		return DashboardStateDTO(widgets=[], layout=[])
	return DashboardStateDTO(widgets=record.widgets or [], layout=record.layout or [])

@router.put("/me/dashboard")
def save_my_dashboard(state: DashboardStateDTO, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
	user_id = str(current_user.id)
	record = db.query(UserDashboard).filter(UserDashboard.user_id == user_id).first()
	if not record:
		record = UserDashboard(user_id=user_id, widgets=state.widgets, layout=[lp.dict() for lp in state.layout])
		db.add(record)
	else:
		record.widgets = [w.dict() for w in state.widgets]
		record.layout = [lp.dict() for lp in state.layout]
	db.commit()
	return {"status": "ok"}