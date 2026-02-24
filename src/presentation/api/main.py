import os
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.di import container
from src.infrastructure.logging.logger import get_logger
from src.presentation.api.schemas.response import HealthResponse

logger = get_logger(__name__)


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    environment = os.getenv("ENVIRONMENT", "production")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    logger.info(
        "Starting AWS AI Agent API",
        extra={
            "environment": environment,
            "aws_region": aws_region,
            "python_version": os.sys.version,
        },
    )

    try:
        # Initialize DI container
        di_container = container.DIContainer()
        app.state.container = di_container
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down AWS AI Agent API")


app = FastAPI(
    title="AWS AI Agent API",
    description="AI agent solution for stock prices and financial document queries",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the current status and timestamp of the API.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
    )


# AgentCore health check endpoint (required by AgentCore - probes /ping)
@app.get("/ping", tags=["health"])
async def ping():
    """AgentCore health check endpoint."""
    return {"status": "healthy"}
