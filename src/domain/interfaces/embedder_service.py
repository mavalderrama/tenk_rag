import abc


class IEmbedderService(abc.ABC):
    @abc.abstractmethod
    def embed(
        self,
        text: str,
        normalize: bool = True,
    ) -> list[float]:
        """Embeds a given text into a vector representation.

        Args:
            text (str): The input text to be embedded.

        Returns:
            list[float]: The vector representation of the input text.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def batch_embed(
        self,
        **kwargs,
    ) -> dict[str, str]:
        """Embeds a list of texts into a list of vector representations.

        Args:
            **kwargs: Keyword arguments for batch embedding.

        Returns:
            dict[str, str]: A dictionary mapping input S3 URI to output S3 URI.
        """
        raise NotImplementedError
