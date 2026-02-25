from pgvector.django import VectorField
from django.db import models


class Item(models.Model):
    embedding = VectorField(dimensions=3)
