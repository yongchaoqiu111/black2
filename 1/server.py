"""
Black2 Main Server

Main entry point for the Black2 clearing API service.
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

from src.api.routes import router
from src.db.transaction_db import init_db

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Black2 Clearing API",
    description="API for transaction clearing, wallet management, and referral rewards",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup.
    """
    await init_db()
    print("Database initialized successfully")


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Black2 Clearing API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    # Get port from environment or use default 8080
    port = int(os.getenv("PORT", "8080"))
    
    # Run the server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
