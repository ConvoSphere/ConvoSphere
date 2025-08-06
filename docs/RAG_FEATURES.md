# Advanced RAG Features Documentation

## Overview

ConvoSphere provides comprehensive Retrieval-Augmented Generation (RAG) capabilities with multiple strategies, configurable parameters, and advanced features for optimal document retrieval and context generation.

## RAG Strategies

### 1. Semantic Retrieval ✅
Uses embedding-based similarity search to find semantically relevant content.

**Features:**
- Vector similarity search using embeddings
- Configurable similarity thresholds
- Support for multiple embedding models
- Context-aware query expansion

**Configuration:**
```json
{
    "strategy": "semantic",
    "embedding_model": "text-embedding-3-small",
    "similarity_threshold": 0.7,
    "max_results": 5
}
```

### 2. Hybrid Retrieval ✅
Combines semantic and keyword search for comprehensive results.

**Features:**
- Weighted combination of semantic and keyword scores
- Configurable weighting parameters
- Automatic query analysis and optimization
- Result deduplication and ranking

**Configuration:**
```json
{
    "strategy": "hybrid",
    "semantic_weight": 0.7,
    "keyword_weight": 0.3,
    "embedding_model": "text-embedding-3-small",
    "similarity_threshold": 0.6
}
```

### 3. Keyword Retrieval ✅
Traditional keyword-based search with advanced text processing.

**Features:**
- Full-text search with exact phrase matching
- Fuzzy search with typo tolerance
- Boolean operators support
- Relevance scoring based on term frequency

**Configuration:**
```json
{
    "strategy": "keyword",
    "fuzzy_threshold": 0.8,
    "boost_exact_matches": true,
    "use_synonyms": true
}
```

### 4. Contextual Retrieval ✅
Uses conversation history to provide context-aware retrieval.

**Features:**
- Conversation history analysis
- Context window management
- Query expansion based on previous interactions
- Temporal relevance scoring

**Configuration:**
```json
{
    "strategy": "contextual",
    "context_window": 10,
    "history_weight": 0.3,
    "temporal_decay": 0.1
}
```

### 5. Adaptive Retrieval ✅
Dynamically selects the best retrieval strategy based on query analysis.

**Features:**
- Automatic query type detection
- Strategy selection based on query characteristics
- Performance monitoring and optimization
- Fallback mechanisms

**Configuration:**
```json
{
    "strategy": "adaptive",
    "query_analysis": true,
    "performance_monitoring": true,
    "fallback_strategy": "hybrid"
}
```

## Embedding Models

### Supported Models ✅

1. **OpenAI Text Embedding 3 Small**
   - Dimensions: 1536
   - Max tokens: 8191
   - Performance: Fast, good quality

2. **OpenAI Text Embedding 3 Large**
   - Dimensions: 3072
   - Max tokens: 8191
   - Performance: Slower, higher quality

3. **OpenAI Ada-002**
   - Dimensions: 1536
   - Max tokens: 8191
   - Performance: Legacy model, still effective

4. **Sentence Transformers MiniLM**
   - Dimensions: 384
   - Max tokens: 256
   - Performance: Very fast, local processing

## Ranking Methods

### 1. Relevance Ranking ✅
Standard relevance scoring based on similarity and content quality.

**Factors:**
- Semantic similarity score
- Keyword match frequency
- Content freshness
- Source authority

### 2. Diversity Ranking ✅
Ensures diverse results by penalizing similar content.

**Features:**
- Content similarity penalty
- Source diversity bonus
- Topic distribution optimization
- Redundancy reduction

### 3. Authority Ranking ✅
Prioritizes content from authoritative sources.

**Features:**
- Source credibility scoring
- Author reputation weighting
- Citation-based authority
- Domain expertise recognition

### 4. Freshness Ranking ✅
Prioritizes recent content with configurable decay.

**Features:**
- Temporal decay functions
- Recency bonuses
- Update frequency consideration
- Time-based relevance

## Advanced Features

### 1. Caching System ✅
Intelligent caching for improved performance.

**Features:**
- Query result caching
- Embedding cache
- Configurable cache expiration
- Cache invalidation strategies

### 2. Performance Monitoring ✅
Comprehensive metrics and analytics.

**Metrics:**
- Retrieval time
- Processing time
- Cache hit rates
- Strategy effectiveness
- User satisfaction scores

### 3. Query Analysis ✅
Advanced query processing and optimization.

**Features:**
- Query type detection
- Intent recognition
- Query expansion
- Synonym handling
- Stop word removal

### 4. Context Management ✅
Intelligent context window management.

**Features:**
- Dynamic context sizing
- Content chunking optimization
- Context overlap management
- Memory-efficient processing

## Configuration Examples

### Basic Configuration
```json
{
    "name": "Default RAG Config",
    "strategy": "hybrid",
    "max_context_length": 4000,
    "max_results": 5,
    "similarity_threshold": 0.7,
    "embedding_model": "text-embedding-3-small",
    "ranking_method": "relevance",
    "cache_results": true
}
```

### Advanced Configuration
```json
{
    "name": "Technical Documents Config",
    "strategy": "adaptive",
    "max_context_length": 6000,
    "max_results": 8,
    "similarity_threshold": 0.6,
    "embedding_model": "text-embedding-3-large",
    "ranking_method": "diversity",
    "cache_results": true,
    "query_analysis": true,
    "performance_monitoring": true,
    "context_window": 15,
    "temporal_decay": 0.05
}
```

### Conversation-Specific Configuration
```json
{
    "name": "Conversation Context Config",
    "strategy": "contextual",
    "max_context_length": 3000,
    "max_results": 3,
    "similarity_threshold": 0.8,
    "embedding_model": "text-embedding-3-small",
    "ranking_method": "relevance",
    "context_window": 10,
    "history_weight": 0.4,
    "temporal_decay": 0.1
}
```

## API Usage Examples

### Basic RAG Query
```python
import requests

response = requests.post("/api/v1/rag/query", json={
    "query": "What is machine learning?",
    "conversation_id": "conv_123",
    "config_id": "default",
    "max_results": 5
})
```

### Advanced RAG Query with Custom Config
```python
response = requests.post("/api/v1/rag/query", json={
    "query": "Explain neural networks",
    "conversation_id": "conv_123",
    "strategy": "hybrid",
    "max_results": 8,
    "similarity_threshold": 0.6,
    "embedding_model": "text-embedding-3-large",
    "include_sources": True,
    "include_metadata": True
})
```

### RAG Configuration Management
```python
# Create new configuration
config_response = requests.post("/api/v1/rag/configs", json={
    "name": "My Custom Config",
    "strategy": "adaptive",
    "max_context_length": 5000,
    "embedding_model": "text-embedding-3-small"
})

# Get metrics
metrics_response = requests.get("/api/v1/rag/metrics")
```

## Best Practices

### 1. Strategy Selection
- **Semantic**: Best for conceptual queries and content discovery
- **Hybrid**: Good balance for most use cases
- **Keyword**: Best for exact phrase matching and technical terms
- **Contextual**: Best for ongoing conversations
- **Adaptive**: Best for varied query types

### 2. Performance Optimization
- Use appropriate embedding models for your use case
- Enable caching for frequently accessed content
- Monitor performance metrics regularly
- Adjust similarity thresholds based on content quality

### 3. Quality Improvement
- Use diversity ranking for comprehensive results
- Implement proper content chunking
- Regular model updates and retraining
- User feedback integration

### 4. Configuration Management
- Create domain-specific configurations
- Regular configuration review and updates
- A/B testing for strategy effectiveness
- Performance-based optimization

## Troubleshooting

### Common Issues

1. **Low Retrieval Quality**
   - Check similarity threshold settings
   - Verify embedding model selection
   - Review content chunking strategy

2. **Slow Performance**
   - Enable caching
   - Use faster embedding models
   - Optimize context window size

3. **Inconsistent Results**
   - Check ranking method configuration
   - Verify query preprocessing
   - Review content quality

### Performance Tuning

1. **Monitor Metrics**
   - Track retrieval times
   - Monitor cache hit rates
   - Analyze strategy effectiveness

2. **Optimize Configuration**
   - Adjust similarity thresholds
   - Fine-tune ranking parameters
   - Optimize context window sizes

3. **Content Quality**
   - Improve document chunking
   - Enhance metadata quality
   - Regular content updates