import pytest

from codeforces_editorial.parsers.url_parser import URLParser, parse_problem_url
from codeforces_editorial.models import ProblemIdentifier
from codeforces_editorial.utils.exceptions import URLParseError


# --- Test Parsing (The Regex) --- #


@pytest.mark.parametrize(
    "url, expected_contest, expected_problem, expected_gym",
    [
        # 1. Standard Contest URL
        ("https://codeforces.com/contest/1234/problem/A", "1234", "A", False),
        # 2. Gym URL
        ("https://codeforces.com/gym/102942/problem/F", "102942", "F", True),
        # 3. Problemset URL
        ("https://codeforces.com/problemset/problem/500/A", "500", "A", False),
        # 4. Russian Domain (.ru)
        ("https://codeforces.ru/contest/1234/problem/C", "1234", "C", False),
        # 5. Complex Problem Index (e.g., B1, C2)
        ("https://codeforces.com/contest/1350/problem/B1", "1350", "B1", False),
    ],
)
def test_parse_valid_urls(url, expected_contest, expected_problem, expected_gym) -> None:
    """Test that all valid URL formats are parsed correctly."""

    identifier = URLParser.parse(url=url)

    # test contest
    assert identifier.contest_id == expected_contest
    # test problem
    assert identifier.problem_id == expected_problem
    # test gym
    assert identifier.is_gym == expected_gym


def test_parse_invalid_urls() -> None:
    """Test that invalid URL raise URLParseError."""

    invalid_urls = [
        "not_a_url",  # wrong url
        "https://google.com",  # wrong site
        "https://codeforces.com/blog/entry/123",  # Valid site, wrong page
        "https://codeforces.com/contest/abc/problem/A",  # Non-numeric contest ID
    ]

    for url in invalid_urls:
        with pytest.raises((URLParseError)):
            URLParser.parse(url=url)


# --- Test URL Building --- #


def test_build_problem_url() -> None:
    """Test that problem URL is built correctly."""

    # Standard Contest
    contest_id = ProblemIdentifier(contest_id="1234", problem_id="A", is_gym=False)
    assert (
        URLParser.build_problem_url(identifier=contest_id)
        == "https://codeforces.com/contest/1234/problem/A"
    )

    # Gym contest
    gym_id = ProblemIdentifier(contest_id="100001", problem_id="B", is_gym=True)
    assert (
        URLParser.build_problem_url(identifier=gym_id)
        == "https://codeforces.com/gym/100001/problem/B"
    )


def test_build_contest_url() -> None:
    """Test that contest URL is built correctly"""

    # Standard Contest
    contest_id = ProblemIdentifier(contest_id="1234", problem_id="A", is_gym=False)
    assert (
        URLParser.build_contest_url(identifier=contest_id) == "https://codeforces.com/contest/1234"
    )

    # Gym contest
    gym_id = ProblemIdentifier("99999", "Z", is_gym=True)
    assert URLParser.build_contest_url(identifier=gym_id) == "https://codeforces.com/gym/99999"


# --- Test Convenience Function --- #

def test_parse_convenience_function() -> None:
    """Test the standalone parse_problem_url function"""

    url = "https://codeforces.com/contest/777/problem/A"
    identifier = parse_problem_url(url)
    assert identifier.contest_id == "777"
    assert identifier.problem_id == "A"
