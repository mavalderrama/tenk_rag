import boto3

from src.domain.interfaces import auth
from botocore.config import Config
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CognitoService(auth.IAuthService):
    def __init__(
        self,
        user_pool_id: str,
        app_client_id: str,
        region: str,
    ):
        config = Config(region_name=region)
        self._cognito_client = boto3.client("cognito-idp", config=config)
        self._user_pool_id = user_pool_id
        self._app_client_id = app_client_id

    def create_user(
        self, username: str, password: str, email: str, temp_password: str
    ) -> None:

        try:
            response = self._cognito_client.admin_create_user(
                UserPoolId=self._user_pool_id,
                Username=username,
                TemporaryPassword=password if temp_password else None,
                UserAttributes=[{"Name": "email", "Value": email}],
                MessageAction="SUPPRESS",  # Don't send welcome email
            )
            if not temp_password:
                # Set permanent password
                self._cognito_client.admin_set_user_password(
                    UserPoolId=self._user_pool_id,
                    Username=username,
                    Password=password,
                    Permanent=True,
                )

            user = response.get("User", {})
            for attr in user.get("Attributes", []):
                if attr["Name"] == "sub":
                    return attr["Value"]

            raise RuntimeError("User sub not found in response")

        except Exception as e:
            raise RuntimeError(f"Failed to create user: {str(e)}")

    def authenticate(self, username: str, password: str) -> dict[str, str]:
        logger.info("Attempting user authentication", extra={"username": username})

        try:
            response = self._cognito_client.initiate_auth(
                ClientId=self._app_client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )

            auth_result = response.get("AuthenticationResult")
            if not auth_result:
                logger.error(
                    "Authentication failed - no auth result",
                    extra={"username": username},
                )
                raise ValueError("Authentication failed")

            logger.info("User authenticated successfully", extra={"username": username})
            return {
                "access_token": auth_result.get("AccessToken", ""),
                "id_token": auth_result.get("IdToken", ""),
                "refresh_token": auth_result.get("RefreshToken", ""),
            }

        except Exception as e:
            logger.error(
                "Authentication failed",
                extra={"username": username, "error": str(e)},
            )
            raise ValueError(f"Authentication failed: {str(e)}")

    def verify_token(self, token: str) -> bool:
        pass
