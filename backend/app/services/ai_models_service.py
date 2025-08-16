from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.models.ai_model import AIModel


class AIModelsService:
	def __init__(self, db: Session):
		self.db = db

	def list_models(self) -> List[AIModel]:
		return self.db.query(AIModel).order_by(AIModel.display_name.asc()).all()

	def get_model(self, model_id: str) -> Optional[AIModel]:
		return self.db.query(AIModel).filter(AIModel.id == model_id).first()

	def create_model(self, data: dict) -> AIModel:
		instance = AIModel(**data)
		self.db.add(instance)
		self.db.commit()
		self.db.refresh(instance)
		return instance

	def update_model(self, model_id: str, data: dict) -> Optional[AIModel]:
		instance = self.get_model(model_id)
		if not instance:
			return None
		for k, v in data.items():
			if hasattr(instance, k):
				setattr(instance, k, v)
		self.db.commit()
		self.db.refresh(instance)
		return instance

	def delete_model(self, model_id: str) -> bool:
		instance = self.get_model(model_id)
		if not instance:
			return False
		self.db.delete(instance)
		self.db.commit()
		return True

	def toggle_active(self, model_id: str, is_active: bool) -> Optional[AIModel]:
		return self.update_model(model_id, {"is_active": is_active})

	def set_default(self, model_id: str) -> Optional[AIModel]:
		instance = self.get_model(model_id)
		if not instance:
			return None
		# clear other defaults
		self.db.query(AIModel).update({AIModel.is_default: False})
		instance.is_default = True
		self.db.commit()
		self.db.refresh(instance)
		return instance