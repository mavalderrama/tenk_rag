import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    ENVIRONMENT: str = "production"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_SESSION_TOKEN: str | None = None

    # Observability Configuration
    OBSERVABILITY_PROVIDER: str = "langfuse"
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_BASE_URL: str = "https://us.langfuse.com"

    LANGSMITH_API_KEY: str = ""
    LANGSMITH_TRACING: bool = False if OBSERVABILITY_PROVIDER == "langfuse" else True
    LANGSMITH_WORKSPACE_ID: str = "aws-ai-agent"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_CALLBACKS_BACKGROUND: bool = False

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        allow_mutation = False
        validate_assignment = True


settings = Settings()
