"""Parser for Codeforces problem URLs."""

import re
from loguru import logger
from domain.models.problem import ProblemIdentifier
from domain.exceptions import URLParsingError


class URLParser:
    """Parser for various Codeforces URL formats."""

    # Unified pattern matches: problemset/problem/1234/A
    PATTERN = r"codeforces\.(?:com|ru)/problemset/problem/(\d+)/([A-Z]\d*)"

    @classmethod
    def parse(cls, url: str) -> ProblemIdentifier:
        """Parse Codeforces problem URL and extract problem identifier."""
        logger.debug(f"Parsing URL: {url}")

        match = re.search(cls.PATTERN, url)
        if match:
            contest_id, index = match.groups()
            identifier = ProblemIdentifier(
                contest_id=contest_id,
                problem_index=index,  # use problem_index now
            )
            logger.info(f"Parsed URL to problem: {identifier}")
            return identifier

        raise URLParsingError(
            f"Unrecognized Codeforces URL format: {url}. "
            "Expected format: https://codeforces.com/problemset/problem/<contest_id>/<problem>"
        )

    @classmethod
    def build_problem_url(cls, identifier: ProblemIdentifier) -> str:
        """Build problem URL from identifier."""
        url = f"https://codeforces.com/problemset/problem/{identifier.contest_id}/{identifier.problem_index}"
        logger.debug(f"Built problem URL: {url}")
        return url

    @classmethod
    def build_contest_url(cls, identifier: ProblemIdentifier) -> str:
        """Build contest main page URL from identifier."""
        url = f"https://codeforces.com/contest/{identifier.contest_id}"
        logger.debug(f"Built contest URL: {url}")
        return url

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Check if URL is a valid Codeforces problem URL."""
        try:
            cls.parse(url)
            return True
        except URLParsingError:
            return False


def parse_problem_url(url: str) -> ProblemIdentifier:
    """Convenience function to parse problem URL."""
    return URLParser.parse(url)
