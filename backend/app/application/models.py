from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db.models import GeneratedField
from pgvector.django import HnswIndex, VectorField


class Documents(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DocumentChunks(models.Model):
    id = models.BigAutoField(primary_key=True)
    document_id = models.ForeignKey(Documents, on_delete=models.PROTECT)
    embedding = VectorField(dimensions=1024)
    search_vector = GeneratedField(
        expression=SearchVector('text', config='english'),
        output_field=SearchVectorField(),
        db_persist=True, # This is the Django equivalent of the "STORED" keyword in your SQL
    )
    text = models.TextField()
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            HnswIndex(
                fields=["embedding"],
                name="document_chunks_embedding_idx",
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
            GinIndex(fields=["search_vector"], name="idx_chunks_search"),
            GinIndex(fields=["metadata"], name="idx_chunks_metadata"),
        ]
