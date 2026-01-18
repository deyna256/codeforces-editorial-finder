from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EditorialRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        if "codeforces.com" not in v and "codeforces.ru" not in v:
            raise ValueError("URL must be a Codeforces URL")
        return v


class EditorialSchema(BaseModel):
    problem_id: str
    solution_text: str
    source_url: Optional[str] = None
    extracted_at: datetime


class ProblemSchema(BaseModel):
    contest_id: str
    problem_id: str
    title: str
    url: str
    contest_name: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None


class EditorialResponse(BaseModel):
    problem: ProblemSchema
    editorial: EditorialSchema
