import asyncio
import time

import httpx
from tenacity import (
    AsyncRetrying,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ai_model import AI
from wiki_parser import ArticleParser

MAX_LEVEL = 1
CONCURRENT_WORKERS = 20
START_URL = 'https://ru.wikipedia.org/wiki/Python'

processed = set()
failed = set()


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, max=2),
    retry=retry_if_exception_type(
        (httpx.ConnectError, httpx.HTTPError, httpx.ReadError, httpx.TimeoutException)
    ),
)
async def fetch_and_parse(
    url: str, client: httpx.AsyncClient, queue: asyncio.Queue, level: int = 0
):
    try:
        response = await client.get(url, timeout=5.0)
        response.raise_for_status()
        article = ArticleParser(response.text, url, level=level)
        parced_page = await asyncio.to_thread(article.article_collect_data)
        print(
            f"✅ Успешно: {url}\n{parced_page.get('title')}\nlevel:{article.level}\nСвязанных ссылок:{len(article.article_related_urls)}\n--------------------"
        )
        print(f"Всего обработанно ссылок:{len(processed)}")
        if article.level < MAX_LEVEL:
            for new_url in article.article_related_urls:
                if new_url not in processed and new_url not in failed:
                    await queue.put((new_url, article.level + 1))
                    processed.add(new_url)
    except Exception as e:
        print(f"❌ Ошибка на {url}: {e}")
        failed.add(url)


async def worker(name: str, queue: asyncio.Queue, client: httpx.AsyncClient):
    while True:
        url, level = await queue.get()
        await fetch_and_parse(url, client, queue, level)
        queue.task_done()


async def main():
    start_time = time.time()
    queue = asyncio.Queue()
    await queue.put((START_URL, 0))

    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(CONCURRENT_WORKERS):
            task = asyncio.create_task(worker(f"worker-{i}", queue, client))
            tasks.append(task)

        await queue.join()
        for task in tasks:
            task.cancel()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Всего обработанно ссылок:{len(processed)}")
    print(f"Всего не валидных ссылок:{len(failed)}")
    print(f"Время выполнения: {execution_time:.4f} секунд")


if __name__ == "__main__":
    asyncio.run(main())
