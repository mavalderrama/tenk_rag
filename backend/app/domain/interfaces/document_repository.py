import abc

from backend.app.domain.dtos import document_chunk as dc


class IDocumentRepository(abc.ABC):
    @abc.abstractmethod
    def search_documents(
        self,
        query_text: str,
        query_embeddings: list[float],
        metadata: dict[str, str | int],
        top_k: int = 10,
    ) -> list[dc.DocumentChunk]:
        """Gets a document by its ID."""
        raise NotImplementedError
