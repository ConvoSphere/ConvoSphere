from sqlalchemy import Boolean, Column, Float, Integer, String

from .base import BaseModel, get_json_column


class AIModel(BaseModel):
	__tablename__ = "ai_models"

	name = Column(String(200), nullable=False)
	provider = Column(String(100), nullable=False)
	model_key = Column(String(200), nullable=False)  # e.g., "gpt-4", "claude-3"
	display_name = Column(String(200), nullable=False)
	description = Column(String(500), nullable=True)
	max_tokens = Column(Integer, nullable=True)
	cost_per_1k_tokens = Column(Float, nullable=True)
	is_active = Column(Boolean, nullable=False, default=True)
	is_default = Column(Boolean, nullable=False, default=False)
	is_favorite = Column(Boolean, nullable=False, default=False)
	capabilities = Column(get_json_column(), nullable=False, default=list)
	performance = Column(get_json_column(), nullable=True)  # optional cached stats