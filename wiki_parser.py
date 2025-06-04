import asyncio
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from AI_MODEL import AI

base_url = "https://ru.wikipedia.org"


class ArticleParser:
    """
    Парсер статьи Википедии на основе HTML-текста страницы.

    Инициализация:
        response_text (str): HTML-код страницы статьи.
        article_url (str): URL самой статьи (для формирования абсолютных ссылок).

    Атрибуты:
        soup (BeautifulSoup): Парсер HTML-документа.
        url (str): URL статьи.
        article_soup (BeautifulSoup | None): Секция страницы с содержимым статьи.
        article_text (str | None): Текст статьи, собранный из тегов <p>.
        article_related_urls (list[str] | None): Список абсолютных URL связанных статей.
        title (str | None): Заголовок статьи (тег <title>).
    """

    def __init__(self, response_text: str, article_url: str):
        self.soup = BeautifulSoup(response_text, 'lxml')
        self.url = article_url
        self.article_soup = None
        self.article_text = None
        self.article_related_urls = None
        self.title = None

    def article_health_check(self) -> bool:
        article_soup = self.soup.find(
            "div", {"class": "mw-content-ltr mw-parser-output"}
        )
        if not article_soup:
            return False
        else:
            self.article_soup = article_soup
            return True

    def get_article_title(self) -> str:
        self.title = self.soup.title.text
        return self.title

    def get_article_text_and_realyted_articls(self) -> tuple[str, list]:
        paragraphs_list = []
        urls_list = []

        for p in self.article_soup.find_all('p'):
            paragraphs_list.append(p.text)
            for a in p.find_all('a', title=True, href=re.compile("^/wiki/")):
                if a:
                    urls_list.append(urljoin(base_url, href))
        if paragraphs_list:
            self.article_text = "\n".join(paragraphs_list)
        self.article_related_urls = urls_list
        return self.article_text, self.article_related_urls

    def article_collect_data(self) -> dict | None:
        if self.article_health_check():
            self.get_article_title()
            self.get_article_text_and_realyted_articls()
            return {
                "title": self.title,
                "text": self.article_text,
                "related_urls": self.article_related_urls,
            }
        else:
            return None
