import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from tortoise.contrib.fastapi import register_tortoise

from app.configs.logger_config import LOGGING_CONFIG
from app.configs.redis_config import get_redis
from app.configs.tortoise_config import TORTOISE_ORM
from app.db.models import WikiArticls
from app.db.pydentic_models import (
    WikiArticle_Pydantic,
    WikiArticleIn_Pydantic,
    WikiArticleSummary_Pydantic,
)
from app.tasks import parser_wrapper

load_dotenv()

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    logger.info("FastAPI app started")
    redis_client = await get_redis()
    yield
    await redis_client.aclose()
    logger.info("FastAPI app stopped")


app = FastAPI(lifespan=lifespan)


async def get_redis_client():
    return redis_client


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)


@app.post(
    "/articles/",
    description="Запускате рекурсивный парсер на основе полученного url",
    summary="Запуск парсера",
)
async def run_parser(
    url: str = Query(..., description=" Стартровый url"),
):
    parser_wrapper.send(url)
    return {"status": "Парсинг запущен!"}


@app.get(
    "/articles/summary",
    response_model=WikiArticleSummary_Pydantic,
    description="Получение summary статьи по её url",
    summary="Summary статьи",
)
async def articles_summary(url: str = Query(..., description="url статьи")):
    article_obj = await WikiArticls.filter(url=url).first()
    if not article_obj:
        raise HTTPException(status_code=404, detail="Article not found")
    return await ArticleSummary_Pydantic.from_tortoise_orm(article_obj)
