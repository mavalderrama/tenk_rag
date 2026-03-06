import pydantic


class AgentResult(pydantic.BaseModel):
    answer: str
    sources: list[str] = []
