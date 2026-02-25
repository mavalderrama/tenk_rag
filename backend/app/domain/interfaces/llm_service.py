import abc

from langchain_core.language_models import BaseChatModel


class ILLMService(abc.ABC):
    @abc.abstractmethod
    def get_llm(self) -> BaseChatModel:
        """Generates a response based on a given prompt."""
        raise NotImplementedError
