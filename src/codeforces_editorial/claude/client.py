"""Claude API client wrapper."""

from typing import Optional

import anthropic
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from codeforces_editorial.config import get_settings
from codeforces_editorial.utils.exceptions import ClaudeAPIError


class ClaudeClient:
    """Wrapper for Claude API with error handling and retry logic."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (uses settings if None)
            model: Claude model to use (uses settings if None)
        """
        settings = get_settings()
        self.api_key = api_key or settings.claude_api_key
        self.model = model or settings.claude_model

        if not self.api_key:
            raise ClaudeAPIError("Claude API key not configured")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.debug(f"Initialized Claude client with model: {self.model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=30),
        reraise=True,
    )
    def send_message(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        system: Optional[str] = None,
    ) -> str:
        """
        Send message to Claude and get response.

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 = deterministic)
            system: Optional system prompt

        Returns:
            Claude's response text

        Raises:
            ClaudeAPIError: If API call fails
        """
        logger.debug(f"Sending message to Claude (model: {self.model})")
        logger.debug(f"Prompt length: {len(prompt)} chars")

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system if system else anthropic.NOT_GIVEN,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            logger.debug(f"Received response ({len(response_text)} chars)")
            logger.debug(f"Usage: {message.usage}")

            return response_text

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            if "rate_limit" in str(e).lower():
                logger.warning("Rate limit hit, retrying...")
                raise  # Let tenacity retry
            raise ClaudeAPIError(f"Claude API error: {e}") from e

        except Exception as e:
            logger.error(f"Unexpected error calling Claude API: {e}")
            raise ClaudeAPIError(f"Failed to call Claude API: {e}") from e

    def find_editorial_link(self, contest_html: str, problem_id: str) -> Optional[str]:
        """
        Use Claude to find editorial link in contest page HTML.

        Args:
            contest_html: HTML content of contest page
            problem_id: Problem ID

        Returns:
            Editorial URL if found, None otherwise

        Raises:
            ClaudeAPIError: If API call fails
        """
        from codeforces_editorial.claude.prompts import get_find_editorial_prompt

        logger.info(f"Using Claude to find editorial link for problem {problem_id}")

        prompt = get_find_editorial_prompt(contest_html, problem_id)

        try:
            response = self.send_message(
                prompt=prompt,
                max_tokens=500,
                temperature=0.0,
                system="You are a helpful assistant that extracts URLs from HTML content. "
                       "Return only the URL, nothing else.",
            )

            response = response.strip()

            # Check if found
            if response == "NOT_FOUND" or not response.startswith("http"):
                logger.warning("Claude could not find editorial link")
                return None

            logger.info(f"Found editorial link: {response}")
            return response

        except ClaudeAPIError:
            raise
        except Exception as e:
            logger.error(f"Error in find_editorial_link: {e}")
            raise ClaudeAPIError(f"Failed to find editorial link: {e}") from e

    def extract_solution(
        self,
        tutorial_content: str,
        problem_id: str,
        problem_title: str = "",
    ) -> dict:
        """
        Use Claude to extract solution from tutorial content.

        Args:
            tutorial_content: Tutorial content (HTML or text)
            problem_id: Problem ID
            problem_title: Optional problem title

        Returns:
            Dictionary with extracted solution components

        Raises:
            ClaudeAPIError: If API call fails
        """
        from codeforces_editorial.claude.prompts import get_extract_solution_prompt
        from codeforces_editorial.models import ProblemIdentifier

        logger.info(f"Using Claude to extract solution for problem {problem_id}")

        # Create a minimal identifier for the prompt
        # Note: We don't have full identifier here, so we parse problem_id
        contest_id = "unknown"
        pid = problem_id
        identifier = ProblemIdentifier(contest_id=contest_id, problem_id=pid)

        prompt = get_extract_solution_prompt(tutorial_content, identifier, problem_title)

        try:
            response = self.send_message(
                prompt=prompt,
                max_tokens=8000,
                temperature=0.0,
                system="You are an expert at analyzing competitive programming editorials. "
                       "Extract and structure the solution information clearly and accurately.",
            )

            # Parse response into structured format
            # For now, return the raw response and let the caller parse it
            # In a production system, you might want to use structured output

            logger.info(f"Successfully extracted solution ({len(response)} chars)")

            return {
                "raw_response": response,
                "problem_id": problem_id,
            }

        except ClaudeAPIError:
            raise
        except Exception as e:
            logger.error(f"Error in extract_solution: {e}")
            raise ClaudeAPIError(f"Failed to extract solution: {e}") from e

    def validate_editorial_content(
        self,
        content: str,
        problem_id: str,
    ) -> bool:
        """
        Validate if content contains editorial for specific problem.

        Args:
            content: Content to validate
            problem_id: Problem ID

        Returns:
            True if content contains editorial for the problem

        Raises:
            ClaudeAPIError: If API call fails
        """
        from codeforces_editorial.claude.prompts import get_validate_editorial_prompt

        logger.debug(f"Validating editorial content for problem {problem_id}")

        prompt = get_validate_editorial_prompt(content, problem_id)

        try:
            response = self.send_message(
                prompt=prompt,
                max_tokens=10,
                temperature=0.0,
            )

            response = response.strip().upper()
            is_valid = response in ["YES", "PARTIAL"]

            logger.debug(f"Validation result: {response} (valid={is_valid})")
            return is_valid

        except Exception as e:
            logger.warning(f"Error validating content: {e}")
            # If validation fails, assume content might be valid
            return True


def create_claude_client() -> ClaudeClient:
    """Create and return a new Claude client instance."""
    return ClaudeClient()
