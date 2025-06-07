import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI, Query
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from app.configs.logger_config import LOGGING_CONFIG
from app.configs.tortoise_config import TORTOISE_ORM
from app.models import WikiArticls

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI app started")
    yield
    logger.info("FastAPI app stopped")


app = FastAPI(lifespan=lifespan)


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)

Article_Pydantic = pydantic_model_creator(WikiArticls, name="WikiArticls")
ArticleIn_Pydantic = pydantic_model_creator(
    WikiArticls, name="ArticleIn", exclude_readonly=True
)


@app.post("/articles", response_model=Article_Pydantic)
async def create_article(article: ArticleIn_Pydantic):
    article_obj = await WikiArticls.create(**article.model_dump())
    return await Article_Pydantic.from_tortoise_orm(article_obj)


@app.get("/articles/", response_model=Article_Pydantic)
async def search_articles(url: str = Query(...)):
    article_obj = await WikiArticls.filter(url=url).first()
    return await Article_Pydantic.from_tortoise_orm(article_obj)
