from langfuse import get_client
from langfuse.langchain import CallbackHandler

from app.domain.interfaces.observability import IObservability
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class LangfuseObservability(IObservability):
    def __init__(self) -> None:
        self.client = get_client()
        if self.client.auth_check():
            logger.info("Langfuse client is authenticated and ready!")
        else:
            logger.error("Authentication failed. Please check your credentials and host.")
        self._handler = CallbackHandler()

    def get_observability_handler(self) -> CallbackHandler:
        return self._handler

    def flush(self) -> None:
        self.client.shutdown()

    def __repr__(self) -> str:
        return f"LangfuseObservability(client={self.client})"
