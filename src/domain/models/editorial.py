# src/domain/models/editorial.py
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from .problem import ProblemIdentifier

@dataclass
class CodeSnippet:
    code: str
    language: str
    description: Optional[str] = None

@dataclass
class Editorial:
    problem: ProblemIdentifier
    approach: str
    algorithm: str
    time_complexity: str
    space_complexity: str
    code_snippets: List[CodeSnippet]
    hints: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    extracted_at: datetime = datetime.now()

@dataclass
class CachedEditorial:
    problem_id: str
    tutorial_text: str
    last_updated: datetime

# --- Add this ---
@dataclass
class TutorialData:
    title: str
    content: str
