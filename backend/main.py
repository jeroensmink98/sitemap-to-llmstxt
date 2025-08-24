from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .celery_app import celery_app
import redis
import os

app = FastAPI(
    title="Sitemap to LLMS.txt API",
    description="Convert sitemaps to LLMS.txt format with background processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        redis_client.ping()
        
        # Check Celery worker status
        celery_stats = celery_app.control.inspect().stats()
        
        return {
            "status": "healthy",
            "redis": "connected",
            "celery_workers": len(celery_stats) if celery_stats else 0
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Sitemap to LLMS.txt API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }