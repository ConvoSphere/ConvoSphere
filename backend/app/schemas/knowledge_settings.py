from pydantic import BaseModel, Field


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
