from sqlalchemy import Boolean, Column, Integer, String

from .base import Base, get_json_column


class KnowledgeSettings(Base):
	__tablename__ = "knowledge_settings"

	# Using single-row table for global settings (id from Base UUIDMixin)
	chunk_size = Column(Integer, nullable=False, default=500)
	chunk_overlap = Column(Integer, nullable=False, default=50)
	embedding_model = Column(String(200), nullable=False, default="text-embedding-ada-002")
	index_type = Column(String(50), nullable=False, default="hybrid")
	metadata_extraction = Column(Boolean, nullable=False, default=True)
	auto_tagging = Column(Boolean, nullable=False, default=True)
	search_algorithm = Column(String(50), nullable=False, default="hybrid")
	max_file_size = Column(Integer, nullable=False, default=10 * 1024 * 1024)
	supported_file_types = Column(get_json_column(), nullable=False, default=list)
	processing_timeout = Column(Integer, nullable=False, default=300)
	batch_size = Column(Integer, nullable=False, default=10)
	enable_cache = Column(Boolean, nullable=False, default=True)
	cache_expiry = Column(Integer, nullable=False, default=3600)