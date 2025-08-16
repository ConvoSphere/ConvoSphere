from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.knowledge_settings import KnowledgeSettings
from backend.app.api.v1.endpoints.knowledge_settings import KnowledgeBaseSettingsModel


class KnowledgeSettingsService:
	def __init__(self, db: Session):
		self.db = db

	def get_settings(self) -> KnowledgeBaseSettingsModel:
		instance = self.db.query(KnowledgeSettings).first()
		if instance is None:
			# Initialize from defaults
			cfg = get_settings().knowledge_base
			instance = KnowledgeSettings(
				chunk_size=getattr(cfg, "chunk_size", 500),
				chunk_overlap=getattr(cfg, "chunk_overlap", 50),
				embedding_model=getattr(cfg, "default_embedding_model", "text-embedding-ada-002"),
				index_type="hybrid",
				metadata_extraction=True,
				auto_tagging=True,
				search_algorithm="hybrid",
				max_file_size=getattr(cfg, "max_file_size", 10 * 1024 * 1024),
				supported_file_types=getattr(cfg, "supported_file_types", []),
				processing_timeout=300,
				batch_size=10,
				enable_cache=True,
				cache_expiry=3600,
			)
			self.db.add(instance)
			self.db.commit()
			self.db.refresh(instance)

		return KnowledgeBaseSettingsModel(
			chunkSize=instance.chunk_size,
			chunkOverlap=instance.chunk_overlap,
			embeddingModel=instance.embedding_model,
			indexType=instance.index_type,
			metadataExtraction=instance.metadata_extraction,
			autoTagging=instance.auto_tagging,
			searchAlgorithm=instance.search_algorithm,
			maxFileSize=instance.max_file_size,
			supportedFileTypes=list(instance.supported_file_types or []),
			processingTimeout=instance.processing_timeout,
			batchSize=instance.batch_size,
			enableCache=instance.enable_cache,
			cacheExpiry=instance.cache_expiry,
		)

	def update_settings(self, payload: KnowledgeBaseSettingsModel) -> KnowledgeBaseSettingsModel:
		instance = self.db.query(KnowledgeSettings).first()
		if instance is None:
			instance = KnowledgeSettings()
			self.db.add(instance)

		instance.chunk_size = payload.chunkSize
		instance.chunk_overlap = payload.chunkOverlap
		instance.embedding_model = payload.embeddingModel
		instance.index_type = payload.indexType
		instance.metadata_extraction = payload.metadataExtraction
		instance.auto_tagging = payload.autoTagging
		instance.search_algorithm = payload.searchAlgorithm
		instance.max_file_size = payload.maxFileSize
		instance.supported_file_types = payload.supportedFileTypes
		instance.processing_timeout = payload.processingTimeout
		instance.batch_size = payload.batchSize
		instance.enable_cache = payload.enableCache
		instance.cache_expiry = payload.cacheExpiry

		self.db.commit()
		self.db.refresh(instance)
		return self.get_settings()