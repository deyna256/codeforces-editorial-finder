"""Prompts for OpenAI API interactions."""

from codeforces_editorial.models import ProblemIdentifier


def get_find_editorial_prompt(contest_html: str, problem_id: str) -> str:
    """
    Get prompt for finding editorial link in contest page HTML.

    Args:
        contest_html: HTML content of contest page
        problem_id: Problem ID to find editorial for

    Returns:
        Prompt string
    """
    return f"""I need you to find the link to the tutorial/editorial/разбор for this Codeforces contest.

The editorial might be called:
- Tutorial
- Editorial
- Разбор (Russian)
- Solutions
- Analysis
- Problem Analysis

Please analyze the provided HTML and find the URL to the editorial. The editorial is usually:
1. A blog post linked from the contest page
2. In the "Contest materials" or similar section
3. Contains links to problem solutions

Return ONLY the full URL to the editorial (starting with http:// or https://), nothing else.
If you cannot find it, return "NOT_FOUND".

HTML content:
{contest_html[:50000]}
"""


def get_extract_solution_prompt(
    tutorial_content: str,
    identifier: ProblemIdentifier,
    problem_title: str = "",
) -> str:
    """
    Get prompt for extracting solution for specific problem from tutorial.

    Args:
        tutorial_content: Tutorial content (HTML or text)
        identifier: Problem identifier
        problem_title: Optional problem title for better matching

    Returns:
        Prompt string
    """
    problem_ref = f"Problem {identifier.problem_id}"
    if problem_title:
        problem_ref += f" ({problem_title})"

    return f"""Extract the editorial/solution for {problem_ref} from the provided tutorial content.

Problem Details:
- Contest ID: {identifier.contest_id}
- Problem ID: {identifier.problem_id}
- Full ID: {identifier.full_id}
{f"- Title: {problem_title}" if problem_title else ""}

Please extract and structure the solution with the following sections:

1. **Problem Understanding**: Brief summary of what the problem asks
2. **Approach**: High-level approach to solve the problem
3. **Algorithm/Data Structure**: Specific algorithm or data structure used
4. **Time Complexity**: Big-O time complexity
5. **Space Complexity**: Big-O space complexity
6. **Detailed Solution**: Step-by-step explanation of the solution
7. **Code**: Any code examples (preserve language and formatting)
8. **Hints** (if available): Progressive hints given in the editorial
9. **Notes** (if available): Additional observations or edge cases

Important:
- Look for sections marked with "{identifier.problem_id}" or "{identifier.full_id}"
- The problem might be referenced as "Problem {identifier.problem_id}", "Task {identifier.problem_id}", etc.
- Code blocks might be in C++, Python, Java or other languages - preserve them exactly
- If complexity is not explicitly stated, try to infer it from the solution
- If a section is not available, you can skip it

Tutorial content:
{tutorial_content[:100000]}

Please provide a comprehensive extraction in a structured format."""


def get_parse_pdf_editorial_prompt(problem_id: str) -> str:
    """
    Get prompt for analyzing PDF editorial.

    Args:
        problem_id: Problem ID

    Returns:
        Prompt string
    """
    return f"""This PDF contains editorial/tutorial for Codeforces problems.

Please extract the solution for Problem {problem_id}.

Include:
1. Problem understanding
2. Solution approach
3. Algorithm/technique used
4. Time and space complexity
5. Detailed explanation
6. Code if available
7. Any hints or notes

Format the response in a clear, structured way."""


def get_alternative_search_prompt(page_html: str) -> str:
    """
    Get prompt for alternative editorial search strategies.

    Args:
        page_html: HTML to search

    Returns:
        Prompt string
    """
    return f"""I'm looking for links to problem tutorials/editorials/solutions on this Codeforces page.

Please find ANY links that might lead to:
- Blog posts with solutions
- Tutorial posts
- Editorial announcements
- Problem analysis
- Solution discussions

Return a JSON list of URLs you find, or empty list [] if none found.
Format: ["url1", "url2", ...]

HTML:
{page_html[:50000]}
"""


def get_validate_editorial_prompt(content: str, problem_id: str) -> str:
    """
    Get prompt to validate if content contains editorial for specific problem.

    Args:
        content: Content to validate
        problem_id: Problem ID

    Returns:
        Prompt string
    """
    return f"""Does this content contain a solution/editorial for Problem {problem_id}?

Please answer with:
- "YES" if it clearly contains a solution or editorial for Problem {problem_id}
- "NO" if it doesn't contain solution for this specific problem
- "PARTIAL" if it mentions the problem but doesn't provide complete solution

Content:
{content[:20000]}
"""
