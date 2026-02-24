import json
import uuid
from datetime import datetime

import boto3

from src.domain.interfaces import distributed_cache, embedder_service
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class BedrockEmbedder(embedder_service.IEmbedderService):
    def __init__(
        self,
        aws_region: str,
        bedrock_batch_client_arn: str,
        bedrock_embedder_model_id: str,
        dimensions: int = 1024,
        cache_client: distributed_cache.IDistributedCache = None,
    ):
        self._bedrock_live_client = boto3.client("bedrock-runtime")
        self._bedrock_batch_client = boto3.client("bedrock")
        self._bedrock_batch_client_arn = bedrock_batch_client_arn
        self._aws_region = aws_region
        self._bedrock_embedder_model_id = bedrock_embedder_model_id
        self._dimensions = dimensions
        self._cache_client = cache_client

    def embed(
        self,
        text: str,
        normalize: bool = True,
    ) -> list[float]:

        body = json.dumps(
            {
                "inputText": text,
                "dimensions": self._dimensions,  # Optional: 256, 512, or 1024
                "normalize": True,  # Recommended for RAG/similarity search
            }
        )

        response = self._bedrock_live_client.invoke_model(
            body=body,
            contentType="application/json",
            accept="application/json",
            modelId=self._bedrock_embedder_model_id,
        )
        try:
            return json.loads(response["body"].read().decode("utf-8"))["embedding"]
        except KeyError as e:
            raise ValueError(f"Unexpected response format from Bedrock: {e}")
        except Exception as e:
            raise RuntimeError(f"Error during embedding: {e}")

    def batch_embed(
        self,
        **kwargs,
    ) -> dict[str, str]:
        timestamp = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        job_id = f"titan-batch-embedding-job-{timestamp}-{uuid.uuid4().hex}"

        input_s3_uri = kwargs.get("input_s3_uri")
        output_s3_uri = kwargs.get("output_s3_uri")

        if not input_s3_uri or not output_s3_uri:
            raise ValueError("Input and output S3 URIs must be provided")

        logger.info(f"Starting Batch Embeddings Job with ID: {job_id}")

        response = self._bedrock_batch_client.create_model_invocation_job(
            jobName=job_id,
            modelId=self._bedrock_embedder_model_id,
            roleArn=self._bedrock_batch_client_arn,
            inputDataConfig={"s3InputDataConfig": {"s3Uri": input_s3_uri}},
            outputDataConfig={"s3OutputDataConfig": {"s3Uri": output_s3_uri}},
        )

        self._cache_client.set(job_id, output_s3_uri)

        logger.info(f"Batch Embeddings Job ARN: {response['jobArn']}")

        return response

    def handle_bedrock_batch_job_state_change(self, event):
        logger.info(f"Received Bedrock Batch Job State Change: {event}")
        if event["detail"]["status"] == "Completed":
            logger.info("Bedrock Batch Job Completed Successfully")

        elif event["detail"]["status"] == "Failed":
            logger.error("Bedrock Batch Job Failed")
