from litestar import Controller, post
from litestar.di import Provide
from loguru import logger

from api.schemas import EditorialRequest, EditorialResponse, ProblemSchema, EditorialSchema
from api.dependencies import provide_http_client, provide_ai_client, provide_cache_client
from services.editorial import get_editorial
from infrastructure.http_client import AsyncHTTPClient
from infrastructure.openai_client import AsyncOpenAIClient
from infrastructure.cache_redis import AsyncRedisCache


class EditorialController(Controller):
    path = "/editorial"
    dependencies = {
        "http_client": Provide(provide_http_client),
        "ai_client": Provide(provide_ai_client),
        "cache": Provide(provide_cache_client),
    }

    @post("/")
    async def get_editorial_endpoint(
        self,
        data: EditorialRequest,
        http_client: AsyncHTTPClient,
        ai_client: AsyncOpenAIClient,
        cache: tuple[AsyncRedisCache | None, bool],
    ) -> EditorialResponse:
        logger.info(f"Received editorial request for URL: {data.url}")

        cache_client, use_cache = cache

        editorial, problem_data = await get_editorial(
            url=data.url,
            http_client=http_client,
            ai_client=ai_client,
            cache_client=cache_client,
            use_cache=use_cache,
        )

        response = EditorialResponse(
            problem=ProblemSchema(
                contest_id=problem_data.identifier.contest_id,
                problem_id=problem_data.identifier.problem_id,
                title=problem_data.title,
                url=problem_data.url,
                contest_name=problem_data.contest_name,
                tags=problem_data.tags,
                time_limit=problem_data.time_limit,
                memory_limit=problem_data.memory_limit,
            ),
            editorial=EditorialSchema(
                problem_id=editorial.problem_id,
                solution_text=editorial.solution_text,
                source_url=editorial.source_url,
                extracted_at=editorial.extracted_at,
            ),
        )

        logger.info(f"Editorial extraction completed for {problem_data.identifier}")
        return response
