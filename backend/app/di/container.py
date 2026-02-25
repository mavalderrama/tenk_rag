import os


class DIContainer:
    def __init__(self):
        # Observability Configuration
        self.observability_provider = os.getenv(
            "OBSERVABILITY_PROVIDER", "langfuse"
        )  # langfuse or langsmith

        # Langfuse Configuration
        self.langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        self.langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        # LangSmith Configuration
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY", "")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "aws-ai-agent")
        self.langsmith_endpoint = os.getenv(
            "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
        )

        # Initialize singletons
        self._stock_repository = None
        self._document_repository = None
        self._observability_service = None
        self._cognito_service = None
        self._agent_orchestrator = None

    @property
    def stock_repository(self):
        return self._stock_repository

    @property
    def document_repository(self):
        return self._document_repository

    @property
    def observability_service(self):
        return self._observability_service

    @property
    def cognito_service(self):
        return self._cognito_service

    @property
    def agent_orchestrator(self):
        return self._agent_orchestrator
