from tortoise.contrib.pydantic import pydantic_model_creator

from .models import WikiArticls

WikiArticleSummary_Pydantic = pydantic_model_creator(
    WikiArticls, name="WikiArticleSummary", exclude=("id", "url", "title", "text")
)


WikiArticle_Pydantic = pydantic_model_creator(WikiArticls, name="WikiArticls")


WikiArticleIn_Pydantic = pydantic_model_creator(
    WikiArticls, name="ArticleIn", exclude_readonly=True
)
