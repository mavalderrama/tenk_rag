import pydantic
from datetime import datetime


class QueryResponse(pydantic.BaseModel):
    """Response schema for agent queries (non-streaming)."""

    query: str
    answer: str
    # reasoning_steps: list[AgentStepResponse]
    sources: list[str]
    execution_time_ms: float
    timestamp: datetime
    trace_id: str | None = None
    trace_url: str | None = None


class AuthResponse(pydantic.BaseModel):
    """Response schema for authentication."""

    access_token: str = pydantic.Field(..., description="JWT access token")
    id_token: str = pydantic.Field(..., description="JWT ID token")
    refresh_token: str = pydantic.Field(..., description="JWT refresh token")
    token_type: str = pydantic.Field(default="Bearer", description="Token type")
    expires_in: int = pydantic.Field(
        default=3600, description="Token expiration in seconds"
    )


class HealthResponse(pydantic.BaseModel):
    """Response schema for health check."""

    status: str = pydantic.Field(..., description="Health status")
    timestamp: datetime = pydantic.Field(..., description="Server timestamp")
    version: str = pydantic.Field(default="1.0.0", description="API version")


class ErrorResponse(pydantic.BaseModel):
    """Response schema for errors."""

    error: str = pydantic.Field(..., description="Error message")
    detail: str | None = pydantic.Field(None, description="Detailed error information")
    timestamp: datetime = pydantic.Field(default_factory=datetime.now)
