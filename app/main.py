"""
FastAPI Application Entry Point

Main application setup with middleware, routing, and error handling
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.routes import connection, policy
from app.utils.exceptions import (
    FirewallException,
    PolicyNotFoundException,
    PolicyAlreadyExistsException,
    ConnectionNotFoundException
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    
    Handles startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info("All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI-Driven Firewall Backend Service
    
    This service provides real-time network connection evaluation using:
    - Rule-based security policies
    - AI-powered anomaly detection
    - Intelligent decision engine
    
    ## Features
    
    * **Policy Management**: Create, update, and manage security policies
    * **Connection Evaluation**: Real-time security decisions for network connections
    * **AI Integration**: Machine learning-based anomaly scoring
    * **Decision Engine**: Intelligent combination of policies and AI insights
    
    ## Decision Logic
    
    1. Check if connection matches any security policy
    2. If policy action is **allow** or **block** → immediate decision
    3. If policy action is **alert** or no match → AI scoring
    4. Apply AI thresholds: >0.8=block, 0.5-0.8=alert, <0.5=allow
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware for cross-origin requests
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS enabled")


# Exception handlers

@app.exception_handler(PolicyNotFoundException)
async def policy_not_found_handler(request: Request, exc: PolicyNotFoundException):
    """Handle policy not found errors"""
    logger.warning(f"Policy not found: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


@app.exception_handler(PolicyAlreadyExistsException)
async def policy_exists_handler(request: Request, exc: PolicyAlreadyExistsException):
    """Handle policy already exists errors"""
    logger.warning(f"Policy already exists: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)}
    )


@app.exception_handler(ConnectionNotFoundException)
async def connection_not_found_handler(request: Request, exc: ConnectionNotFoundException):
    """Handle connection not found errors"""
    logger.warning(f"Connection not found: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


@app.exception_handler(FirewallException)
async def firewall_exception_handler(request: Request, exc: FirewallException):
    """Handle general firewall service errors"""
    logger.error(f"Firewall error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal firewall service error"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(connection.router)
app.include_router(policy.router)


# Health check endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health check endpoint",
    response_description="Service health status"
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    
    Returns basic service status and version information
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="Root endpoint",
    response_description="Welcome message"
)
async def root():
    """
    Root endpoint with service information
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
