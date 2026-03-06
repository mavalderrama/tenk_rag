import pydantic


class DocumentChunk(pydantic.BaseModel):
    document_id: str
    text: str
    score: float
    metadata: dict[str, str | int] = {}
