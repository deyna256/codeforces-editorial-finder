from loguru import logger

from domain.models import Editorial, CachedEditorial, ProblemData, ProblemIdentifier, TutorialFormat
from domain.parsers.url_parser import URLParser
from domain.parsers.problem_page import ProblemPageParser
from domain.parsers.tutorial_parser import TutorialParser
from domain.fetchers.tutorial_finder import TutorialFinder
from domain.extractors.editorial_extractor import EditorialExtractor
from domain.exceptions import CodeforcesEditorialError


async def get_editorial(
    url: str,
    http_client,
    ai_client,
    cache_client=None,
    use_cache: bool = True,
) -> tuple[Editorial, ProblemData]:
    logger.debug(f"Starting editorial extraction for URL: {url}")

    try:
        identifier = URLParser.parse(url)
        logger.debug(f"Resolved problem identifier: {identifier}")

        if use_cache and cache_client:
            cached_editorial = await _get_from_cache(cache_client, identifier)
            if cached_editorial:
                problem_data = await _parse_problem_page(http_client, identifier)
                return cached_editorial, problem_data

        logger.debug(f"Parsing problem page for {identifier}")
        problem_data = await _parse_problem_page(http_client, identifier)

        logger.debug(f"Finding tutorial for {identifier}")
        tutorial_url = await _find_tutorial(ai_client, http_client, identifier)

        logger.debug(f"Parsing tutorial content from {tutorial_url}")
        tutorial_data = await _parse_tutorial(http_client, tutorial_url)

        logger.debug("Extracting editorial content")
        editorial = await _extract_editorial(
            ai_client,
            tutorial_data,
            identifier,
            problem_data.title,
        )

        if use_cache and cache_client:
            await _save_to_cache(
                cache_client,
                identifier,
                editorial,
                tutorial_url,
                tutorial_data.format,
            )

        logger.info(f"Editorial extraction completed for {identifier}")
        return editorial, problem_data

    except CodeforcesEditorialError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in editorial service: {e}")
        raise CodeforcesEditorialError(f"Failed to get editorial: {e}") from e


async def _parse_problem_page(http_client, identifier: ProblemIdentifier) -> ProblemData:
    parser = ProblemPageParser(http_client)
    return await parser.parse_problem_page(identifier)


async def _find_tutorial(ai_client, http_client, identifier: ProblemIdentifier) -> str:
    finder = TutorialFinder(ai_client, http_client)
    return await finder.find_tutorial(identifier)


async def _parse_tutorial(http_client, tutorial_url: str):
    parser = TutorialParser(http_client)
    return await parser.parse(tutorial_url)


async def _extract_editorial(
    ai_client, tutorial_data, identifier: ProblemIdentifier, problem_title: str
) -> Editorial:
    extractor = EditorialExtractor(ai_client)
    return await extractor.extract(tutorial_data, identifier, problem_title)


async def _get_from_cache(cache_client, identifier: ProblemIdentifier) -> Editorial | None:
    if not cache_client:
        return None

    try:
        cached_data = await cache_client.get(identifier.cache_key)
        if cached_data:
            logger.debug(f"Get editorial for {identifier=} from cache")
            cached = CachedEditorial.from_dict(cached_data)
            return cached.editorial

        logger.debug(f"Cache miss for {identifier.cache_key}")
        return None

    except Exception as e:
        logger.warning(f"Cache retrieval failed: {e}")
        return None


async def _save_to_cache(
    cache_client,
    identifier: ProblemIdentifier,
    editorial: Editorial,
    url: str,
    fmt: TutorialFormat,
) -> None:
    if not cache_client:
        return

    try:
        logger.debug(f"Saving editorial to cache: {identifier.cache_key}")
        cached_editorial = CachedEditorial(
            problem=identifier,
            editorial=editorial,
            tutorial_url=url,
            tutorial_format=fmt,
        )
        cached_data = cached_editorial.to_dict()
        await cache_client.set(identifier.cache_key, cached_data)
    except Exception as e:
        logger.warning(f"Failed to save to cache: {e}")


async def clear_cache(cache_client) -> None:
    if cache_client:
        logger.info("Clearing cache")
        await cache_client.flushdb()
    else:
        logger.warning("Cache is not enabled")
