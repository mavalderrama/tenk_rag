import abc


class IMessage(abc.ABC):
    @abc.abstractmethod
    def consumer(self) -> None:
        """
        Listens for incoming messages and processes them.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_queue(self) -> None:
        """
        Creates a new message queue for handling messages.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        """
        raise NotImplementedError
