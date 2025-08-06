# Knowledge Base Settings

## Overview

ConvoSphere provides comprehensive configuration options for document processing, embedding models, and search algorithms through the Knowledge Base Settings interface.

## Key Features

### Document Processing
- **Chunk Size**: 100-2000 characters per document chunk
- **Chunk Overlap**: 0-500 characters overlap between chunks
- **Max File Size**: Up to 100MB per file
- **Processing Timeout**: 60-3600 seconds
- **Processing Engine**: Traditional, Docling, or Auto-selection
- **Language Detection**: Automatic language detection and processing
- **OCR Support**: Image-based document processing with OCR
- **Audio Transcription**: Speech-to-text for audio files

### Embedding Models
- **OpenAI Ada-002**: 1536 dimensions, 8191 max tokens
- **OpenAI Text Embedding 3 Small**: 1536 dimensions, 8191 max tokens
- **OpenAI Text Embedding 3 Large**: 3072 dimensions, 8191 max tokens
- **Sentence Transformers MiniLM**: 384 dimensions, 256 max tokens
- **Custom Models**: Support for custom embedding models
- **Model Selection**: Automatic model selection based on content type

### Search & Indexing
- **Index Type**: Vector, Hybrid, or Full-text indexing
- **Search Algorithm**: Semantic, Keyword, Hybrid, Fuzzy, or Faceted search
- **Metadata Extraction**: Enable/disable automatic metadata extraction
- **Auto Tagging**: Enable/disable automatic document tagging
- **Search Suggestions**: Enable/disable search autocomplete
- **Search Analytics**: Enable/disable search usage tracking

### Processing Options
- **Batch Size**: 1-100 documents per batch
- **Cache**: Enable/disable processing cache
- **Cache Expiry**: Configurable cache expiration time
- **Background Processing**: Enable/disable background job processing
- **Retry Logic**: Configurable retry attempts for failed processing
- **Error Handling**: Detailed error reporting and recovery options

### RAG Configuration
- **RAG Strategies**: Semantic, Hybrid, Keyword, Contextual, Adaptive
- **Context Window**: 1000-8000 characters for context generation
- **Similarity Threshold**: 0.1-1.0 for result filtering
- **Max Results**: 1-20 results per query
- **Ranking Methods**: Relevance, Diversity, Authority, Freshness
- **Caching**: Enable/disable RAG result caching

### Bulk Operations
- **Max Batch Size**: 10-1000 documents per bulk operation
- **Progress Tracking**: Enable/disable real-time progress updates
- **Error Handling**: Continue on error or stop processing
- **Background Jobs**: Enable/disable background processing for bulk operations

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
  "cacheExpiry": 3600,
  "processingEngine": "auto",
  "languageDetection": true,
  "ocrSupport": true,
  "audioTranscription": true,
  "searchSuggestions": true,
  "searchAnalytics": true,
  "backgroundProcessing": true,
  "retryAttempts": 3,
  "ragStrategy": "hybrid",
  "contextWindow": 4000,
  "similarityThreshold": 0.7,
  "maxResults": 5,
  "rankingMethod": "relevance",
  "ragCaching": true,
  "maxBatchSize": 100,
  "progressTracking": true,
  "continueOnError": true,
  "backgroundJobs": true
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