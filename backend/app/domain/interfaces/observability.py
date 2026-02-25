import abc
from langfuse import langchain


class IObservability(abc.ABC):
    @abc.abstractmethod
    def get_observability_handler(self) -> langchain.CallbackHandler:
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self) -> str:
        raise NotImplementedError
