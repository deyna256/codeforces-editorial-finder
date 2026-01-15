from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class ProblemIdentifier:
    contest_id: int
    problem_index: str
    is_gym: bool = False  # default False

    def __init__(
        self,
        contest_id: Union[int, str],
        problem_index: str | None = None,
        *,
        problem: str | None = None,
        problem_id: str | None = None,
        is_gym: bool = False,
    ) -> None:
        # Convert contest_id to int if possible
        if isinstance(contest_id, str):
            try:
                contest_id_int = int(contest_id)
            except ValueError:
                contest_id_int = -1  # fallback for unknown
        else:
            contest_id_int = contest_id

        object.__setattr__(self, "contest_id", contest_id_int)

        # Determine problem index
        index = problem_index or problem or problem_id
        if index is None:
            raise TypeError("ProblemIdentifier requires a problem index")
        object.__setattr__(self, "problem_index", index)

        object.__setattr__(self, "is_gym", is_gym)

    # Backward compatible aliases for tests
    @property
    def problem_id(self) -> str:
        return self.problem_index

    @property
    def full_id(self) -> str:
        return f"{self.contest_id}-{self.problem_index}"

    @property
    def cache_key(self) -> str:
        return f"{self.contest_id}-{self.problem_index}"

@dataclass
class ProblemData:
    identifier: ProblemIdentifier
    title: str
    url: str
    contest_name: str
    possible_editorial_links: Optional[List[str]] = None
    rating: Optional[int] = None
    tags: Optional[List[str]] = None
