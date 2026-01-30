# FastAPI entry point
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print("Starting up...")
    
    yield
    
    # Shutdown
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Project Management Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns:
        dict: Health status and version information
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


# Include routers
from app.api.routes import projects, tasks, documents, chat

app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

# Additional routers (commented out for now, will add as we implement)
# from app.api.routes import teams, integrations
# app.include_router(teams.router, prefix="/teams", tags=["teams"])
# app.include_router(integrations.router, prefix="/integrations", tags=["integrations"])

