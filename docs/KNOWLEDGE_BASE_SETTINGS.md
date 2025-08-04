# Knowledge Base Settings

## Overview

ConvoSphere provides comprehensive configuration options for document processing, embedding models, and search algorithms through the Knowledge Base Settings interface.

## Key Features

### Document Processing
- **Chunk Size**: 100-2000 characters per document chunk
- **Chunk Overlap**: 0-500 characters overlap between chunks
- **Max File Size**: Up to 100MB per file
- **Processing Timeout**: 60-3600 seconds

### Embedding Models
- **OpenAI Ada-002**: 1536 dimensions, 8191 max tokens
- **OpenAI Text Embedding 3 Small**: 1536 dimensions, 8191 max tokens
- **OpenAI Text Embedding 3 Large**: 3072 dimensions, 8191 max tokens
- **Sentence Transformers MiniLM**: 384 dimensions, 256 max tokens

### Search & Indexing
- **Index Type**: Vector or Hybrid indexing
- **Search Algorithm**: Semantic, Keyword, or Hybrid search
- **Metadata Extraction**: Enable/disable automatic metadata extraction
- **Auto Tagging**: Enable/disable automatic document tagging

### Processing Options
- **Batch Size**: 1-100 documents per batch
- **Cache**: Enable/disable processing cache
- **Cache Expiry**: Configurable cache expiration time

## Configuration

### Access Settings
1. Navigate to Knowledge Base
2. Click on Settings tab
3. Configure desired options
4. Click "Save Settings"

### API Endpoints
- `GET /api/v1/knowledge/settings` - Get current settings
- `PUT /api/v1/knowledge/settings` - Update settings

### Default Values
```json
{
  "chunkSize": 500,
  "chunkOverlap": 50,
  "embeddingModel": "text-embedding-ada-002",
  "indexType": "hybrid",
  "metadataExtraction": true,
  "autoTagging": true,
  "searchAlgorithm": "hybrid",
  "maxFileSize": 10485760,
  "processingTimeout": 300,
  "batchSize": 10,
  "enableCache": true,
  "cacheExpiry": 3600
}
```

## Best Practices

### Performance Optimization
- Use smaller chunk sizes (200-500) for better search precision
- Enable cache for frequently accessed documents
- Use hybrid search for best results

### Cost Optimization
- Choose appropriate embedding model based on needs
- Disable auto-tagging if not needed
- Set reasonable processing timeouts

### Quality Settings
- Use larger chunk sizes (800-1200) for better context
- Enable metadata extraction for better organization
- Use hybrid indexing for comprehensive search