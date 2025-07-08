#!/usr/bin/env python3
"""
Test script for AI integration.

This script tests the AI service, Assistant Engine, and related components
to ensure they are working correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.ai_service import AIService, ai_service
from app.services.assistant_engine import AssistantEngine, ContextWindow, AssistantContext
from app.services.assistant_service import AssistantService
from app.services.conversation_service import ConversationService
from app.services.tool_service import ToolService
from app.core.database import get_db
from app.core.config import settings


async def test_ai_service():
    """Test basic AI service functionality."""
    print("🧪 Testing AI Service...")
    
    # Test AI service initialization
    if not ai_service.is_enabled():
        print("❌ AI service is disabled")
        return False
    
    print("✅ AI service is enabled")
    
    # Test health check
    health = ai_service.health_check()
    print(f"✅ Health check: {health}")
    
    # Test available models
    models = ai_service.get_available_models()
    print(f"✅ Available models: {len(models)}")
    
    # Test available providers
    providers = ai_service.get_available_providers()
    print(f"✅ Available providers: {len(providers)}")
    
    return True


async def test_assistant_engine():
    """Test Assistant Engine functionality."""
    print("\n🧪 Testing Assistant Engine...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize services
        assistant_service = AssistantService(db)
        conversation_service = ConversationService(db)
        tool_service = ToolService(db)
        
        # Create assistant engine
        engine = AssistantEngine(
            ai_service=ai_service,
            assistant_service=assistant_service,
            conversation_service=conversation_service,
            tool_service=tool_service
        )
        
        print("✅ Assistant Engine created")
        
        # Test context manager
        context_manager = engine.get_context_manager()
        print("✅ Context Manager available")
        
        # Test tool executor
        tool_executor = engine.get_tool_executor()
        print("✅ Tool Executor available")
        
        return True
        
    except Exception as e:
        print(f"❌ Assistant Engine test failed: {e}")
        return False
    finally:
        db.close()


async def test_embeddings():
    """Test embedding generation."""
    print("\n🧪 Testing Embeddings...")
    
    try:
        # Test single embedding
        text = "This is a test sentence for embedding generation."
        embedding = await ai_service.get_embeddings(text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Single embedding generated: {len(embedding)} dimensions")
        else:
            print("❌ Single embedding failed")
            return False
        
        # Test batch embeddings
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        embeddings = await ai_service.get_embeddings_batch(texts)
        
        if embeddings and len(embeddings) == len(texts):
            print(f"✅ Batch embeddings generated: {len(embeddings)} embeddings")
        else:
            print("❌ Batch embeddings failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False


async def test_chat_completion():
    """Test chat completion functionality."""
    print("\n🧪 Testing Chat Completion...")
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! How are you today?"}
        ]
        
        response = await ai_service.chat_completion(
            messages=messages,
            model="gpt-3.5-turbo",  # Use a cheaper model for testing
            max_tokens=100
        )
        
        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"✅ Chat completion successful: {content[:50]}...")
            return True
        else:
            print("❌ Chat completion failed")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion test failed: {e}")
        return False


async def test_rag_completion():
    """Test RAG-enhanced completion."""
    print("\n🧪 Testing RAG Completion...")
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What can you tell me about AI?"}
        ]
        
        response = await ai_service.chat_completion_with_rag(
            messages=messages,
            user_id="test-user",
            model="gpt-3.5-turbo",
            max_tokens=100,
            use_knowledge_base=True,
            use_tools=False
        )
        
        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"✅ RAG completion successful: {content[:50]}...")
            return True
        else:
            print("❌ RAG completion failed")
            return False
            
    except Exception as e:
        print(f"❌ RAG completion test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting AI Integration Tests...")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Default AI model: {settings.default_ai_model}")
    
    # Run tests
    tests = [
        test_ai_service,
        test_assistant_engine,
        test_embeddings,
        test_chat_completion,
        test_rag_completion
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n📊 Test Results:")
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {i+1}. {test.__name__}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 