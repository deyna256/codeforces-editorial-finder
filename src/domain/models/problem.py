from dataclasses import dataclass
from typing import List

@dataclass
class ProblemData:
    name: str
    rating: int
    tags: List[str]

@dataclass
class ProblemIdentifier:
    contest_id: int
    index: str
