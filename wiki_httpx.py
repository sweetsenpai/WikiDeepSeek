import asyncio

import httpx
from tenacity import (
    AsyncRetrying,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from wiki_parser import ArticleParser

processed_urls = {}
failed_urls = set()
not_processed_urls = set()

start_url = 'https://ru.wikipedia.org/wiki/Python'

not_processed_urls.add(start_url)


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, max=2),
    retry=retry_if_exception_type(
        (httpx.ConnectError, httpx.HTTPError, httpx.ReadError, httpx.TimeoutException)
    ),
)
async def fetch(url: str, client: httpx.AsyncClient):
    response = await client.get(url, timeout=5.0)
    response.raise_for_status()
    article = ArticleParser(response.text, url)
    x = await asyncio.to_thread(article.article_collect_data)
    print(x.get('title'))
    return response


async def main():
    async with httpx.AsyncClient() as client:
        tasks = []
        for url in not_processed_urls:
            tasks.append((url, fetch(url, client)))

        results = await asyncio.gather(
            *[task for _, task in tasks], return_exceptions=True
        )

        for (url, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                print(f"❌ Ошибка при обработке {url}: {result}")
                failed_urls.add(url)
            else:
                print(f"✅ Успешно: {url}")
                processed_urls[url] = result

        print(f"\nУспешно получено {len(processed_urls)} страниц.")
        print(f"Не удалось получить: {len(failed_urls)}")
        print(not_processed_urls)


if __name__ == "__main__":
    asyncio.run(main())
