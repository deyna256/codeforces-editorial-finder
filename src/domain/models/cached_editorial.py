# src/domain/models/cached_editorial.py
from dataclasses import dataclass
from .editorial import Editorial

@dataclass
class CachedEditorial:
    editorial: Editorial
    cached_at: str | None = None
