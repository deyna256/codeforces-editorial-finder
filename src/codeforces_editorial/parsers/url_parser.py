"""Parser for Codeforces problem URLs."""

import re
from urllib.parse import urlparse

from loguru import logger

from codeforces_editorial.models import ProblemIdentifier
from codeforces_editorial.utils.exceptions import URLParseError


class URLParser:
    """Parser for various Codeforces URL formats."""

    # Unified pattern matches:
    # 1. contest/1234/problem/A
    # 2. gym/1234/problem/A
    # 3. problemset/problem/1234/A
    PATTERN = (
        r"codeforces\.(?:com|ru)/(?:contest|gym|problemset/problem)/(\d+)(?:/problem)?/([A-Z]\d*)"
    )

    @classmethod
    def parse(cls, url: str) -> ProblemIdentifier:
        """
        Parse Codeforces problem URL and extract problem identifier.

        Args:
            url: Codeforces problem URL

        Returns:
            ProblemIdentifier with contest_id, problem_id, and is_gym flag

        Raises:
            URLParseError: If URL format is not recognized

        Examples:
            >>> URLParser.parse("https://codeforces.com/contest/1234/problem/A")
            ProblemIdentifier(contest_id='1234', problem_id='A', is_gym=False)

            >>> URLParser.parse("https://codeforces.ru/gym/102345/problem/B1")
            ProblemIdentifier(contest_id='102345', problem_id='B1', is_gym=True)
        """
        logger.debug(f"Parsing URL: {url}")

        # Validate URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise URLParseError(f"Invalid URL format: {url}")
        except Exception as e:
            raise URLParseError(f"Failed to parse URL: {url}") from e

        # Single Regex Matching
        match = re.search(cls.PATTERN, url)
        if match:
            # Extraction
            contest_id, problem_id = match.groups()

            # Check if it's a gym problem
            is_gym = "/gym/" in url

            identifier = ProblemIdentifier(
                contest_id=contest_id,
                problem_id=problem_id,
                is_gym=is_gym,
            )

            logger.info(f"Parsed URL to problem: {identifier}")
            return identifier

        # No pattern matched
        raise URLParseError(
            f"Unrecognized Codeforces URL format: {url}. "
            f"Supported formats:\n"
            f"  - https://codeforces.com/contest/<contest_id>/problem/<problem_id>\n"
            f"  - https://codeforces.com/problemset/problem/<contest_id>/<problem_id>\n"
            f"  - https://codeforces.com/gym/<contest_id>/problem/<problem_id>"
        )

    @classmethod
    def build_problem_url(cls, identifier: ProblemIdentifier) -> str:
        """
        Build problem URL from identifier.

        Args:
            identifier: Problem identifier

        Returns:
            Full problem URL
        """
        base = "https://codeforces.com"
        segment = "gym" if identifier.is_gym else "contest"

        url = f"{base}/{segment}/{identifier.contest_id}/problem/{identifier.problem_id}"

        logger.debug(f"Built problem URL: {url}")
        return url

    @classmethod
    def build_contest_url(cls, identifier: ProblemIdentifier) -> str:
        """
        Build contest main page URL from identifier.

        Args:
            identifier: Problem identifier

        Returns:
            Contest main page URL
        """
        base = "https://codeforces.com"
        segment = "gym" if identifier.is_gym else "contest"

        url = f"{base}/{segment}/{identifier.contest_id}"

        logger.debug(f"Built contest URL: {url}")
        return url

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """
        Check if URL is a valid Codeforces problem URL.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            cls.parse(url)
            return True
        except URLParseError:
            return False


def parse_problem_url(url: str) -> ProblemIdentifier:
    """
    Convenience function to parse problem URL.

    Args:
        url: Codeforces problem URL

    Returns:
        ProblemIdentifier
    """
    return URLParser.parse(url)
