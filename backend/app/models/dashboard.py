from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, get_json_column

class UserDashboard(BaseModel):
	__tablename__ = "user_dashboards"

	user_id = Column("user_id", nullable=False, index=True)
	widgets = Column(get_json_column(), nullable=False, default=list)
	layout = Column(get_json_column(), nullable=False, default=list)