from configs.tortoies_config import TORTOISE_ORM
from fastapi import FastAPI
from models import WikiArticls
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

app = FastAPI()

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


@app.get("/articles", response_model=list[Article_Pydantic])
async def get_articles():
    return await Article_Pydantic.from_queryset(WikiArticls.all())
