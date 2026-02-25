# AWS
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
LANGSMITH_TRACING: bool = OBSERVABILITY_PROVIDER != "langfuse"
LANGSMITH_WORKSPACE_ID: str = "aws-ai-agent"
LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
LANGCHAIN_CALLBACKS_BACKGROUND: bool = False
