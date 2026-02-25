from django.db import models
from pgvector.django import VectorField


class Item(models.Model):
    embedding = VectorField(dimensions=3)
