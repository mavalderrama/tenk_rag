import boto3
from langchain_aws import ChatBedrockConverse

from src.domain.interfaces import llm_service


class BedrockLLMService(llm_service.ILLMService):
    def __init__(
        self,
        bedrock_model_id: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        region_name: str = "us-east-2",
    ):
        self._bedrock_live_client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
        )
        self._bedrock_model_id = bedrock_model_id

        self._llm = ChatBedrockConverse(
            client=self._bedrock_live_client,
            model=self._bedrock_model_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def get_llm(self) -> ChatBedrockConverse:
        return self._llm
