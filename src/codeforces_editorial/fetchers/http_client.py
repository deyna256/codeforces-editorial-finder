"""HTTP client with retry logic for fetching web content."""

from typing import Optional

import httpx
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from codeforces_editorial.config import get_settings
from codeforces_editorial.utils.exceptions import NetworkError, ProblemNotFoundError


class HTTPClient:
    """HTTP client with retry logic and error handling."""

    def __init__(self, timeout: Optional[int] = None, user_agent: Optional[str] = None):
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            user_agent: User agent string for requests
        """
        settings = get_settings()
        self.timeout = timeout or settings.http_timeout
        self.user_agent = user_agent or settings.user_agent
        self.retries = settings.http_retries

        self.client = httpx.Client(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
            follow_redirects=True,
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get(self, url: str) -> httpx.Response:
        """
        Perform GET request with retry logic.

        Args:
            url: URL to fetch

        Returns:
            HTTP response

        Raises:
            ProblemNotFoundError: If resource not found (404)
            NetworkError: For other network/HTTP errors
        """
        logger.debug(f"Fetching URL: {url}")

        try:
            response = self.client.get(url)
            response.raise_for_status()
            logger.debug(f"Successfully fetched URL: {url} (status: {response.status_code})")
            return response

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Resource not found: {url}")
                raise ProblemNotFoundError(f"Resource not found: {url}") from e
            logger.error(f"HTTP error for {url}: {e}")
            raise NetworkError(f"HTTP error {e.response.status_code}: {url}") from e

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.warning(f"Network error for {url}: {e}")
            raise  # Let tenacity retry

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            raise NetworkError(f"Failed to fetch {url}: {e}") from e

    def get_text(self, url: str) -> str:
        """
        Fetch URL and return text content.

        Args:
            url: URL to fetch

        Returns:
            Response text content
        """
        response = self.get(url)
        return response.text

    def get_bytes(self, url: str) -> bytes:
        """
        Fetch URL and return binary content.

        Args:
            url: URL to fetch

        Returns:
            Response binary content
        """
        response = self.get(url)
        return response.content

    def get_content_type(self, url: str) -> str:
        """
        Get content type of URL.

        Args:
            url: URL to check

        Returns:
            Content-Type header value
        """
        response = self.get(url)
        return response.headers.get("content-type", "").lower()


def create_http_client() -> HTTPClient:
    """Create and return a new HTTP client instance."""
    return HTTPClient()
