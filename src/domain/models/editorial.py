from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TutorialFormat(str, Enum):
    HTML = "html"
    PDF = "pdf"
    UNKNOWN = "unknown"


class Language(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    AUTO = "auto"


@dataclass
class TutorialData:
    url: str
    format: TutorialFormat
    content: str
    language: Language = Language.AUTO
    title: Optional[str] = None
    author: Optional[str] = None
    raw_bytes: Optional[bytes] = None


@dataclass
class CodeSnippet:
    language: str
    code: str
    description: Optional[str] = None


@dataclass
class Editorial:
    problem_id: str
    solution_text: str
    approach: Optional[str] = None
    algorithm: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    code_snippets: list[CodeSnippet] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    notes: Optional[str] = None
    source_url: Optional[str] = None
    extracted_at: datetime = field(default_factory=datetime.now)
    ai_model: Optional[str] = None


@dataclass
class CachedEditorial:
    editorial: Editorial
    cached_at: datetime = field(default_factory=datetime.now)
    ttl_hours: int = 168

    @property
    def is_expired(self) -> bool:
        age_hours = (datetime.now() - self.cached_at).total_seconds() / 3600
        return age_hours > self.ttl_hours
