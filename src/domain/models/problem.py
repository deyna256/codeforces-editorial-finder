from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ProblemIdentifier:
    contest_id: str
    problem_id: str
    is_gym: bool = False

    @property
    def full_id(self) -> str:
        return f"{self.contest_id}{self.problem_id}"

    @property
    def cache_key(self) -> str:
        return f"problem:{self.full_id}"

@dataclass
class ProblemData:
    identifier: ProblemIdentifier
    title: str
    url: str
    contest_name: Optional[str]
    possible_editorial_links: List[str]
