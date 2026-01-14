# src/domain/models/__init__.py

# Import problem-related models
from .problem import ProblemIdentifier, ProblemData

# Import editorial-related models
from .editorial import TutorialData, Editorial, CachedEditorial

# Explicitly declare exports (optional but good practice)
__all__ = [
    "ProblemIdentifier",
    "ProblemData",
    "TutorialData",
    "Editorial",
    "CachedEditorial"
]
