"""
The Daily Worker - Main Backend Application
FastAPI-based REST API for content management and delivery
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.config import settings, setup_directories
from backend.logging_config import setup_logging

# Initialize logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting The Daily Worker backend")
    setup_directories()

    # Validate configuration
    if not settings.has_llm_api():
        logger.warning("No LLM API keys configured - article generation will not work")

    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Backend: {settings.get_base_url()}")

    yield

    # Shutdown
    logger.info("Shutting down The Daily Worker backend")


# Create FastAPI app
app = FastAPI(
    title="The Daily Worker API",
    description="AI-powered working-class news platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS middleware (allow frontend to access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [f"http://{settings.frontend_host}:{settings.frontend_host}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (images)
# app.mount("/static", StaticFiles(directory=settings.local_image_storage), name="static")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.environment,
            "version": "1.0.0",
            "database": "connected" if True else "disconnected",  # TODO: actual DB check
            "llm_apis": settings.has_llm_api()
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "The Daily Worker API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.debug else None
    }


# API Routes
from backend.routes import articles, editorial

app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(editorial.router, prefix="/api/editorial", tags=["editorial"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
