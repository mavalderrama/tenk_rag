import abc


class IAuthService(abc.ABC):
    @abc.abstractmethod
    def authenticate(self, username: str, password: str) -> dict[str, str]:
        """Authenticates a given token."""
        raise NotImplementedError

    @abc.abstractmethod
    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        temp_password: str,
    ) -> None:
        """Creates a new user."""
        raise NotImplementedError

    @abc.abstractmethod
    def verify_token(self, token: str) -> bool:
        """Verifies the validity of a given token."""
        raise NotImplementedError
