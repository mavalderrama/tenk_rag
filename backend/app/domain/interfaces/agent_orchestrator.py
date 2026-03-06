import abc

from backend.app.domain.dtos import agents


class IAgentOrchestrator(abc.ABC):
    @abc.abstractmethod
    async def run(self, query: str) -> agents.AgentResult:
        raise NotImplementedError
