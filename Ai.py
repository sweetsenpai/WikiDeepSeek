import logging
import os

from dotenv import load_dotenv
from openai import AsyncClient, OpenAIError

logger = logging.getLogger(__name__)
load_dotenv()

key = os.getenv("OPENAI_KEY")
url = os.getenv("OPENAI_URL")


class AI:
    """
    Класс для взаимодействия с моделью искусственного интеллекта
    с целью создания краткого содержания текста.
    """

    def __init__(self, ai_key=key, ai_url=url):
        """
        Инициализирует экземпляр класса AI.

        Args:
            ai_key (str, optional): API-ключ для доступа к ИИ-моделям.
            ai_url (str, optional): Базовый URL сервера с ИИ-моделями.

        Raises:
            RuntimeError: Если не передан хотя бы один из параметров: `ai_key` или `ai_url`.
        """
        self.key = ai_key
        self.url = ai_url

        if not self.key:
            raise RuntimeError("Не переданн api_key")

        if not self.url:
            raise RuntimeError("Не переданн ai_url")

        self.client = AsyncClient(api_key=self.key, base_url=self.url)

    async def __aenter__(self):
        self.client = AsyncClient(api_key=self.key, base_url=self.url)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.close()

    async def get_summary(
        self, text: str, ai_model: str = "mistralai/mistral-7b-instruct"
    ) -> str:
        """
        Генерирует краткое содержание заданного текста с использованием указанной ИИ-модели.

        Args:
            text (str): Текст, для которого необходимо создать краткое содержание.
            ai_model (str, optional): Название используемой ИИ-модели. По умолчанию "mistralai/mistral-7b-instruct".

        Returns:
            str: Краткое содержание текста, сгенерированное моделью.
        """
        try:
            completion = await self.client.chat.completions.create(
                model=ai_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Сделай краткое содержание текста:\n\n{text}",
                    }
                ],
                max_tokens=512,
            )
            return completion.choices[0].message.content
        except OpenAIError as e:
            logger.warning(f"Ошибка при генерации summary: {e}")
            return "[Не удалось сгенерировать краткое содержание]"
