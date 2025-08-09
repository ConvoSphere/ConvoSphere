#!/usr/bin/env python3
"""
Simple backend server for ConvoSphere AI Assistant Platform.
This is a minimal version that can start successfully.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="ConvoSphere AI Assistant Platform",
    description="A comprehensive AI assistant platform with conversation management, knowledge base, and multi-provider AI integration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check model
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ConvoSphere AI Assistant Platform",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="ConvoSphere AI Assistant Platform is running",
        version="1.0.0"
    )

@app.get("/api/v1/health")
async def api_health():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running",
        "version": "1.0.0"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "status": "operational",
        "services": {
            "backend": "running",
            "database": "not_configured",
            "ai_providers": "not_configured",
            "storage": "not_configured"
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Get settings from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"Starting ConvoSphere AI Assistant Platform...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Log Level: {log_level}")
    
    # Start the server
    uvicorn.run(
        "simple_backend:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level.lower(),
    )