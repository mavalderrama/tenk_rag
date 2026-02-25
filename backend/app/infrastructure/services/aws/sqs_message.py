import json

import boto3

from app.domain.interfaces import embedder_service as embedder
from app.domain.interfaces import messages
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class SQSMessage(messages.IMessage):
    def __init__(
        self,
        queue_url: str,
        embedder_service: embedder.IEmbedderService,
    ):
        self._sqs_client = boto3.client("sqs")
        self._queue_url = queue_url
        self._bedrock_embedder = embedder_service
        self.create_queue()

    def create_queue(self) -> None:
        logger.info("Creating SQS queue...")
        try:
            self._sqs_client.create_queue(QueueName=self._queue_url)
        except Exception as e:
            logger.error(f"Failed to create SQS queue: {e}")

    def _process_sqs_message(self, msg_body: str) -> None:
        event = json.loads(msg_body)

        # Check the Source
        source = event.get("source")
        detail_type = event.get("detail-type")

        if source == "aws.bedrock":
            if detail_type == "Bedrock Model Invocation Job State Change":
                self._bedrock_embedder.handle_bedrock_batch_job_state_change(event["detail"])

        else:
            logger.info(f"Received unknown event from: {source}")

    def consumer(self) -> None:
        logger.info("Listening for Bedrock job updates...")
        while True:
            # Long Polling: Waits up to 20 seconds for a message
            response = self._sqs_client.receive_message(
                QueueUrl=self._queue_url,
                WaitTimeSeconds=20,
                MaxNumberOfMessages=1,
            )

            if "Messages" in response:
                for msg in response["Messages"]:
                    # The event body is the JSON from EventBridge
                    body = json.loads(msg["Body"])
                    job_id = body["detail"]["jobArn"]
                    status = body["detail"]["status"]

                    logger.info(f"Notification received: Job {job_id} is {status}")

                    if status == "Completed":
                        self._process_sqs_message(body)

                    # Delete the message so you don't process it twice
                    self._sqs_client.delete_message(
                        QueueUrl=self._queue_url, ReceiptHandle=msg["ReceiptHandle"]
                    )
