from backend.app.domain.dtos import document_chunk as dc
from backend.app.domain.interfaces import document_repository as dr
from backend.app.domain.interfaces import embedder_service


class SearchDocuments:
    def __init__(
        self,
        document_repository: dr.IDocumentRepository,
        embedder: embedder_service.IEmbedderService,
    ):
        self._document_repository = document_repository
        self._embedder = embedder

    def execute(
        self,
        query_text: str,
        metadata: dict[str, str | int],
        max_results: int = 10,
    ) -> list[dc.DocumentChunk]:
        return self._document_repository.search_documents(
            query_text=query_text,
            query_embeddings=self._embedder.embed(query_text),
            metadata=metadata,
            top_k=max_results,
        )
