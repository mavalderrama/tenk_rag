import pydantic


class QueryRequest(pydantic.BaseModel):
    query: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language query for the AI agent",
        examples=["What is the stock price for Amazon right now?"],
    )


class AuthenticateRequest(pydantic.BaseModel):
    username: str = pydantic.Field(..., min_length=1, max_length=2000)
    password: str = pydantic.Field(..., min_length=1, max_length=2000)
