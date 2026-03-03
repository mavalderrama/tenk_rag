import json

from django.db import connection


class PostgresVectorDb:
    def __init__(
        self,
        documents_limit: int = 100,
    ) -> None:
        self._connection = connection
        self._documents_limit = documents_limit

    def execute(
        self,
        query_text: str,
        query_embeddings: list[float],
        metadata: dict[str, str | int],
        top_k: int = 10,
    ) -> list[tuple[str, str]]:

        metadata_json_str = json.dumps(metadata)

        sql = """
            -- 0. PRE-FILTER: Narrow down the dataset using the JSON metadata GIN index
            WITH filtered_chunks AS (
                SELECT id, search_vector, embedding
            FROM application_documentchunks
            WHERE metadata @> %(metadata)s::jsonb
            ),
            -- 1. SPARSE: Search only within the filtered chunks
            keyword_search AS (
                SELECT id,
            RANK() OVER (ORDER BY ts_rank_cd(search_vector, plainto_tsquery('english', %s)) DESC) as rank
            FROM filtered_chunks
            WHERE search_vector @@ plainto_tsquery('english', %(query_text)s)
            LIMIT %(documents_limit)s
            ),
            -- 2. DENSE: Search only within the filtered chunks
            semantic_search AS (
                SELECT id,
            RANK() OVER (ORDER BY embedding <=> %(query_embedings)s::vector) as rank
            FROM filtered_chunks
            LIMIT %(documents_limit)s
            )
            -- 3. RRF FUSION
            SELECT
            c.document_id,
            c.text,
            COALESCE(1.0 / (60 + k.rank), 0.0) + COALESCE(1.0 / (60 + s.rank), 0.0) AS rrf_score
            FROM application_documentchunks c
            JOIN filtered_chunks fc ON c.id = fc.id -- Ensure we only return filtered items
            LEFT JOIN keyword_search k ON c.id = k.id
            LEFT JOIN semantic_search s ON c.id = s.id
            WHERE k.id IS NOT NULL OR s.id IS NOT NULL
            ORDER BY rrf_score DESC
            LIMIT %(top_k)s;
        """

        with self._connection.cursor() as cursor:
            cursor.execute(
                sql,
                params={
                    "metadata": metadata_json_str,
                    "query_text": query_text,
                    "query_embeddings": query_embeddings,
                    "documents_limit": self._documents_limit,
                    "top_k": top_k,
                },
            )

        return [(r[0], r[1], r[2]) for r in cursor.fetchall()]  # type: ignore
