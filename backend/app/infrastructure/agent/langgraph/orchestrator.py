from typing import Annotated, Any, TypedDict

from app.domain.dtos import agents
from langgraph.graph import add_messages

from backend.app.domain.interfaces import agent_orchestrator as ao
from backend.app.domain.interfaces import observability as ob
from backend.app.infrastructure.agent.langgraph import tools


class AgentState(TypedDict):
    """State for the agent graph.

    messages uses Annotated with add_messages reducer so returned messages
    are appended to the list (not replaced). This is critical for the
    Converse API which requires full message history with tool_use/tool_result pairs.
    """

    messages: Annotated[list, add_messages]  # type: ignore
    reasoning_steps: list[dict[str, Any]]
    final_answer: str | None


class Orchestrator(ao.IAgentOrchestrator):
    def __init__(
        self,
        agent_tools: tools.AgentTools,
        observability_provider: ob.IObservability,
    ):
        pass

    async def run(self, query: str) -> agents.AgentResult:
        pass
